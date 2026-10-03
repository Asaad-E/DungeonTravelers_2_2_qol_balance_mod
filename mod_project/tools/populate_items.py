import openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/items.xlsx')
ws = wb['Items']

item_updates = {
    'Croissant': "Restore an ally's HP by 60.",
    'Danish': "Restore an ally's HP by 250.",
    'Bagel Sandwich': "Restore an ally's HP by 500.",
    'Pain Aux Raisins': "Fully restore an ally's HP (9,999 HP).",
    'Gateau Au Chocolat': "Restore all allies' HP by 100.",
    'Sachertorte': "Restore all allies' HP by 200.",
    'Tarte Tatin': "Restore all allies' HP by 500.",
    'Egg Sandwich': "Fluffy egg sandwich. Restores 10 HP to an ally.",
    'Yakisoba-Pan': "Noodle-stuffed bread. Restores 20 HP to an ally.",
    'Premium Steak Sandwich': "Deluxe steak sandwich. Restores 30 HP to an ally.",
    'Maharaja Curry': "Super spicy curry. Restores 150 HP to an ally.",
    'Killer Curry': "Legendary curry. Restores 1,000 HP to an ally.",
    'Magical Fruit': "Restore an ally's TP by 25.",
    'Fairy Apple': "Restore an ally's TP by 50.",
    'Golden Apple': "Restore an ally's TP by 100.",
    'Harunire Leaf': "Cure one status ailment for an ally.",
    'Fumirul Nectar': "Cure all status ailments for an ally.",
    'Mui Kuha Medicine': "Revive a fallen ally with 10% HP.",
    'Hipanera Tea': "Nutritional tea. Restores 50 HP and 50 TP to an ally.",
    'Genghis Khan Hotpot': "Delicious hotpot dish. Restores 150 HP to an ally.",
    'Hong Shao': "Simmered bear paw dish. Restores 300 HP to an ally.",
    'Harihari Hotpot': "Whale and mizuna hotpot. Restores 400 HP to an ally.",
    'Konpeito': "Small rugged candy. Restores 60 HP to an ally.",
    'Galactic Konpeito': "Large-scale konpeito. Restores 120 HP to an ally."
}

count = 0
for row in ws.iter_rows(min_row=2):
    name = row[2].value
    if name in item_updates:
        row[5].value = item_updates[name]
        row[6].value = 'Approved'
        count += 1
        print(f"Updated item: {name} -> {item_updates[name]}")

wb.save('mod_project/data_tables/items.xlsx')
print(f"Successfully updated {count} items in items.xlsx")
