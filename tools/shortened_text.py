"""
Original sentences shortened by hand, so that the sentence and its data fit in one line of 85 characters.

Rule of decided: a text is one line; where the original plus its data does not fit, the original is
made shorter. Each entry keeps the joke or the image of the original and drops only filler. They are
used only when the original does not fit (the generators check), and the build accepts no other
change to an original sentence.

The sentences are not written here: they are the sheets ShortItems, ShortSkills and SkillTemplates of
data_tables/qol_rules.xlsx. Edit them there.
"""
import rules

# item name -> shorter sentence (the data in parentheses is added after it)
ITEM_SENTENCES = rules.pairs('ShortItems', 'Item', 'Sentence')

# skill name -> shorter line 1; its damage word and chance are then added by the usual rules
SKILL_SENTENCES = rules.pairs('ShortSkills', 'Skill', 'Sentence')

# skill name -> (line 1 with places for its figures, labels of the box whose figures go there).
# {dmg} is the damage word. For skills with several effects, where a list at the end would not fit.
# Templates whose figures are values the box below already shows are used only when the setting
# line1_values is yes; those whose figures are chances are always used.
LINE1_VALUES = rules.yes(rules.setting('line1_values'))
SKILL_TEMPLATES = {r['Skill']: (r['Template'], [label.strip() for label in r['Labels'].split('|')])
                   for r in rules.rows('SkillTemplates') if LINE1_VALUES or r['Figures'] == 'chances'}
