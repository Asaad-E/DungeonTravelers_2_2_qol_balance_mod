using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>Part files of the scripts of measures/: a list of rows cut in parallel_workers slices, one file each, read back whole by the report.</summary>
    public static class Parts
    {
        public static int Count(Ctx c) => c.SetInt("parallel_workers");

        public static string Name(Ctx c, string prefix, int k) => c.Path("measures", prefix + "_" + k + ".json");

        /// <summary>Removes the files of the earlier pass and writes slice k of n of the rows as `json.dump(rows, f, indent=1)`.</summary>
        public static void Write(Ctx c, string prefix, List<object> rows)
        {
            int n = Count(c);
            foreach (var name in M.Listing(c.Path("measures"))) if (name.StartsWith(prefix + "_") && name.EndsWith(".json")) File.Delete(c.Path("measures", name));
            for (int k = 1; k <= n; k++) c.WriteText(Name(c, prefix, k), PyJson.Dump(Ctx.Slice(rows, k, n), 1), false);
        }

        /// <summary>glob('measures/prefix_*.json'): the rows of every file, in the order of the names.</summary>
        public static List<Obj> Read(Ctx c, string prefix)
        {
            var rows = new List<Obj>();
            foreach (var name in M.Listing(c.Path("measures")))
                if (name.StartsWith(prefix + "_") && name.EndsWith(".json")) rows.AddRange(((List<object>)c.ReadJson(c.Path("measures", name))).Cast<Obj>());
            return rows;
        }

        /// <summary>The figures every script keeps of the runs of a cell: share of wins, length of the won fights, HP left.</summary>
        public static Obj Cell(JobResult done)
        {
            var res = done.Runs;
            var won = res.Where(r => r.Won).ToList();
            return new Obj
            {
                { "won", (double)won.Count / res.Length }, { "time", won.Count > 0 ? (object)(Py.Sum(won.Select(r => r.Time)) / won.Count) : null },
                { "hp_left", Py.Sum(res.Select(r => r.HpLeft)) / res.Length }, { "runs", (long)res.Length },
            };
        }

        public static string Mean0(double x) => Py.F(x * 100, 0, true);
    }

    /// <summary>measures/mercenaries.py: what each mercenary adds; measures/MERCENARIES.md.</summary>
    public static class Mercenaries
    {
        public static void Run(Ctx c, int runs = 60)
        {
            var data = c.Data("variant");
            var places = c.In("mercenaries").A("places").Select(x => (string)x).ToList();
            var names = new List<string> { null, "summon" };
            var npcNames = data.Npcs.Select(r => r.Name).Distinct().ToList();
            npcNames.Sort(string.CompareOrdinal);
            names.AddRange(npcNames);
            var jobs = new List<JobSpec>();
            foreach (var name in names)
                foreach (var cid in places)
                    jobs.Add(Jb.Make(c, "variant", cid, runs: runs, crown: 0, guest: name == "summon" ? null : name == null ? "none" : name, name: name + "|" + cid));
            var done = c.RunLoose(jobs);
            int level = c.Sc("variant").ReferenceLevels()["C40"].level;
            var rows = new List<object>();
            int at = 0;
            foreach (var name in names)
            {
                var cells = new Obj();
                foreach (var cid in places)
                {
                    var d = done[at++];
                    cells.Set(cid, d.Error != null ? new Obj { { "error", d.Error } } : Parts.Cell(d));
                }
                object npcLevel = null;
                if (name != null && name != "summon")
                {
                    var mine = data.Npcs.Where(r => r.Name == name).OrderBy(r => r.Level).ToList();
                    var under = mine.Where(r => r.Level <= level).ToList();
                    npcLevel = (long)(under.Count > 0 ? under[under.Count - 1] : mine[0]).Level;
                }
                rows.Add(new Obj { { "guest", name }, { "cells", cells }, { "level", npcLevel } });
            }
            Parts.Write(c, "mercenaries", rows);
        }

        public static void Report(Ctx c)
        {
            var places = c.In("mercenaries").A("places").Select(x => (string)x).ToList();
            var rows = Parts.Read(c, "mercenaries");
            var baseCells = rows.First(r => r.Get("guest") == null).O("cells");
            int minWins = Noise.MinWins(c);
            var scored = new List<(double score, string guest, double wins, double length, double hp, string cells)>();
            var failed = new List<string>();
            foreach (var r in rows)
            {
                if (r.Get("guest") == null) continue;
                var cells = r.O("cells");
                if (places.Any(p => cells.O(p).Has("error"))) { failed.Add(r.S("guest")); continue; }
                double wins = Py.Sum(places.Select(p => cells.O(p).D("won") - baseCells.O(p).D("won"))) / places.Count;
                var lengths = places.Where(p => Noise.LengthReadable(baseCells.O(p), cells.O(p), minWins)).Select(p => 1 - cells.O(p).D("time") / baseCells.O(p).D("time")).ToList();
                double hp = Py.Sum(places.Select(p => cells.O(p).D("hp_left") - baseCells.O(p).D("hp_left"))) / places.Count;
                double length = lengths.Count > 0 ? Py.Sum(lengths) / lengths.Count : 0;
                scored.Add((wins + length, r.S("guest"), wins, length, hp, string.Join(" ", places.Select(p => Py.Pct(cells.O(p).D("won"), 0)))));
            }
            var lines = new List<string>
            {
                "# What each mercenary adds (generated by dtcli mercenaries)", "",
                "The reference party at " + string.Join(", ", places) + " with the guest, against the same party with none (" + string.Join(" ", places.Select(p => Py.Pct(baseCells.O(p).D("won"), 0))) + " of wins).", "",
                "| Guest | Wins at the three | Wins, mean | Fights shorter | HP left |", "|---|---|---|---|---|",
            };
            var ordered = scored.OrderByDescending(x => x.score).ThenByDescending(x => x.guest, StringComparer.Ordinal).ThenByDescending(x => x.wins).ThenByDescending(x => x.length)
                                .ThenByDescending(x => x.hp).ThenByDescending(x => x.cells, StringComparer.Ordinal);
            foreach (var (_, name, wins, length, hp, cells) in ordered)
                lines.Add("| " + (name == "summon" ? "the summon of the grand sealbook" : name) + " | " + cells + " | " + Py.F(wins * 100, 1, true) + " | " + Py.Pct(length, 1, true) + " | " + Py.F(hp * 100, 0, true) + " |");
            if (failed.Count > 0) { lines.Add(""); lines.Add("Not played (the model failed on their record): " + string.Join(", ", failed)); }
            c.WriteText(c.Path("measures", "MERCENARIES.md"), M.Lines(lines), true);
        }
    }

    /// <summary>measures/party_skills.py: what the bonus of each party skill is worth; measures/PARTY_SKILLS.md.</summary>
    public static class PartySkills
    {
        public static void Run(Ctx c, int runs = 100)
        {
            var inp = c.In("party_skills");
            var places = inp.A("places").Select(x => (string)x).ToList();
            var resist = inp.O("resist");
            var skills = inp.O("skills");
            var names = new List<string> { null };
            var sorted = skills.Keys.ToList(); sorted.Sort(string.CompareOrdinal);
            names.AddRange(sorted);
            var jobs = new List<JobSpec>();
            foreach (var name in names)
                foreach (var cid in places)
                {
                    var recipe = new Obj();
                    if (name != null)
                    {
                        var entry = (List<object>)skills[name];
                        var one = new Obj { { "count", entry[0] } };
                        foreach (var kv in (Obj)entry[1])
                        {
                            if (kv.Key == "hp" || kv.Key == "tp") one.Set(kv.Key, kv.Value);
                            else if (resist.Has(kv.Key))
                            {
                                if (!one.Has("resist")) one.Set("resist", new Obj());
                                one.O("resist").Set(Py.Str(resist[kv.Key]), kv.Value);
                            }
                            else
                            {
                                if (!one.Has("stats")) one.Set("stats", new Obj());
                                one.O("stats").Set(kv.Key, kv.Value);
                            }
                        }
                        recipe = new Obj { { "bonuses", Jb.L(one) } };
                    }
                    jobs.Add(Jb.Make(c, "variant", cid, runs: runs, crown: 0, recipe: recipe, name: name + "|" + cid));
                }
            var done = c.Run(jobs);
            var rows = new List<object>();
            int at = 0;
            foreach (var name in names)
            {
                var cells = new Obj();
                foreach (var cid in places) cells.Set(cid, Parts.Cell(done[at++]));
                rows.Add(new Obj { { "skill", name }, { "cells", cells } });
            }
            Parts.Write(c, "party_skills", rows);
        }

        public static void Report(Ctx c)
        {
            var inp = c.In("party_skills");
            var places = inp.A("places").Select(x => (string)x).ToList();
            var skills = inp.O("skills");
            var rows = Parts.Read(c, "party_skills");
            var baseCells = rows.First(r => r.Get("skill") == null).O("cells");
            var scored = new List<(double score, string skill, long count, string bonus, double wins, double length, double hp)>();
            foreach (var r in rows)
            {
                if (r.Get("skill") == null) continue;
                var cells = r.O("cells");
                double wins = Py.Sum(places.Select(p => cells.O(p).D("won") - baseCells.O(p).D("won"))) / places.Count;
                var lengths = places.Where(p => Py.Truthy(cells.O(p).Get("time")) && Py.Truthy(baseCells.O(p).Get("time"))).Select(p => 1 - cells.O(p).D("time") / baseCells.O(p).D("time")).ToList();
                double hp = Py.Sum(places.Select(p => cells.O(p).D("hp_left") - baseCells.O(p).D("hp_left"))) / places.Count;
                var entry = (List<object>)skills[r.S("skill")];
                double length = Py.Sum(lengths) / lengths.Count;
                scored.Add((wins + length, r.S("skill"), (long)Py.Num(entry[0]), string.Join(", ", ((Obj)entry[1]).Select(kv => kv.Key + " +" + Py.Str(kv.Value))), wins, length, hp));
            }
            var lines = new List<string>
            {
                "# What the bonus of each party skill is worth (generated by dtcli party-skills)", "",
                "The reference party at " + string.Join(", ", places) + ", with the full bonus on as many members as the skill needs, against the same party without it. Sorted by wins and length gained.", "",
                "| Party skill | Members | Bonus at every proof | Wins | Fights shorter | HP left |", "|---|---|---|---|---|---|",
            };
            foreach (var (_, name, count, bonus, wins, length, hp) in scored.OrderByDescending(x => x.score).ThenByDescending(x => x.skill, StringComparer.Ordinal).ThenByDescending(x => x.count)
                                                                              .ThenByDescending(x => x.bonus, StringComparer.Ordinal).ThenByDescending(x => x.wins).ThenByDescending(x => x.length).ThenByDescending(x => x.hp))
                lines.Add("| " + name + " | " + count + " | " + bonus + " | " + Py.F(wins * 100, 0, true) + " | " + Py.Pct(length, 0, true) + " | " + Py.F(hp * 100, 0, true) + " |");
            c.WriteText(c.Path("measures", "PARTY_SKILLS.md"), M.Lines(lines), true);
        }
    }
}
