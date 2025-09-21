import csv


def load_csv(path):
    try:
        with open(path, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []

units = load_csv('units.csv')
weapons = load_csv('weapons.csv')
tags = load_csv('tags.csv')
keywords = load_csv('keywords.csv')

tex_content = ''
for unit in units:
    unit_weapons = []
    if unit.get('weapons'):
        weapon_ids = [w for w in unit['weapons'].split(',') if w]
        unit_weapons = [w for w in weapons if w['uuid'] in weapon_ids]
    weapon_rows = ''
    for w in unit_weapons:
        kw_field = w.get('keywords','')
        if kw_field:
            kw_ids = [k for k in kw_field.split(',') if k]
            kw_names = [kobj['name'] for kobj in keywords if kobj['uuid'] in kw_ids]
            keywords_str = ', '.join(kw_names)
        else:
            keywords_str = ''
        weapon_rows += f"{w.get('name','')} & {w.get('R','-')} & {w.get('N','-')} & {w.get('L','-')} & {w.get('M','-')} & {w.get('H','-')} & {w.get('F','-')} & {keywords_str} \\\\ \hline\n"
    tags_str = ''
    if unit.get('tags'):
        tag_ids = [t for t in unit['tags'].split(',') if t]
        tag_names = [tobj['name'] for tobj in tags if tobj['uuid'] in tag_ids]
        tags_str = ', '.join(tag_names)
    tex_content += "\\unitcard{" + unit.get('name','') + "}{" + unit.get('subtitle','') + "}{" + unit.get('M','-') + "}{" + unit.get('A','-') + "}{" + unit.get('C','-') + "}{" + unit.get('H','-') + "}{" + unit.get('MP','-') + "}{" + unit.get('Mat','-') + "}{" + tags_str + "}\n"

    # Abilities injection: use 'None' when empty; convert newlines to LaTeX line breaks
    abilities_raw = unit.get('abilities', '') or ''
    abilities_text = abilities_raw.strip()
    if not abilities_text:
        abilities_text = 'None'
    else:
        abilities_text = abilities_text.replace('\n', ' \\\\ ')

    tex_content += "\\weapontable{" + weapon_rows + "}{" + abilities_text + "}\n\n"
with open('units.tex','w',encoding='utf-8') as f:
    f.write(tex_content)
print('Wrote units.tex')
