import csv
import os
from django.db import migrations

def load_species_from_csv(apps, schema_editor):
    Species = apps.get_model('bio', 'Species')
    
    # Если данные уже загружены, не загружаем их повторно
    if Species.objects.exists():
        print("Species.objects.all()", Species.objects.all())
        return
    
    # Путь к CSV файлу
    csv_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'species.csv')
    
    # Проверка существования файла
    if not os.path.exists(csv_file_path):
        print(f"CSV файл не найден: {csv_file_path}")
        return
    
    # Открываем CSV файл и загружаем данные
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile, delimiter=';')
        
        # Создаем список объектов для массовой вставки
        species_list = []
        
        for row in csv_reader:
            try:
                # Создаем объект Species с соответствующими полями
                # Названия полей должны соответствовать заголовкам в CSV
                species = Species(
                    title=row.get('title', ''),
                    author=row.get('author', ''),
                    
                    # Шкалы Ландольта
                    lLight=row.get('lLight') if row.get('lLight') != '' else None,
                    lTemperature=row.get('lTemperature') if row.get('lTemperature') != '' else None,
                    lContinentality=row.get('lContinentality') if row.get('lContinentality') != '' else None,
                    lMoisture=row.get('lMoisture') if row.get('lMoisture') != '' else None,
                    lReaction=row.get('lReaction') if row.get('lReaction') != '' else None,
                    lNutrient=row.get('lNutrient') if row.get('lNutrient') != '' else None,
                    lHumus=row.get('lHumus') if row.get('lHumus') != '' else None,
                    lDispersion=row.get('lDispersion') if row.get('lDispersion') != '' else None,
                    
                    # Шкалы Элленберга
                    eLight=row.get('eLight') if row.get('eLight') != '' else None,
                    eTemperature=row.get('eTemperature') if row.get('eTemperature') != '' else None,
                    eContinentality=row.get('eContinentality') if row.get('eContinentality') != '' else None,
                    eMoisture=row.get('eMoisture') if row.get('eMoisture') != '' else None,
                    eReaction=row.get('eReaction') if row.get('eReaction') != '' else None,
                    eNutrient=row.get('eNutrient') if row.get('eNutrient') != '' else None,
                    
                    # Шкалы Цыганова
                    tm1=row.get('tm1') if row.get('tm1') != '' else None,
                    tm2=row.get('tm2') if row.get('tm2') != '' else None,
                    kn1=row.get('kn1') if row.get('kn1') != '' else None,
                    kn2=row.get('kn2') if row.get('kn2') != '' else None,
                    om1=row.get('om1') if row.get('om1') != '' else None,
                    om2=row.get('om2') if row.get('om2') != '' else None,
                    cr1=row.get('cr1') if row.get('cr1') != '' else None,
                    cr2=row.get('cr2') if row.get('cr2') != '' else None,
                    hd1=row.get('hd1') if row.get('hd1') != '' else None,
                    hd2=row.get('hd2') if row.get('hd2') != '' else None,
                    tr1=row.get('tr1') if row.get('tr1') != '' else None,
                    tr2=row.get('tr2') if row.get('tr2') != '' else None,
                    nt1=row.get('nt1') if row.get('nt1') != '' else None,
                    nt2=row.get('nt2') if row.get('nt2') != '' else None,
                    rc1=row.get('rc1') if row.get('rc1') != '' else None,
                    rc2=row.get('rc2') if row.get('rc2') != '' else None,
                    lc1=row.get('lc1') if row.get('lc1') != '' else None,
                    lc2=row.get('lc2') if row.get('lc2') != '' else None,
                    fh1=row.get('fh1') if row.get('fh1') != '' else None,
                    fh2=row.get('fh2') if row.get('fh2') != '' else None,
                    
                    # Биологические характеристики
                    raunkiaer=row.get('raunkiaer'),
                    serebryakov=row.get('serebryakov'),
                    ecobiomorphs=row.get('ecobiomorphs'),
                    geoelements=row.get('geoelements'),
                    ta=row.get('ta')
                )
                species_list.append(species)
            except Exception as e:
                continue
            
            # Для оптимизации памяти - вставляем данные пакетами по 1000 записей
            if len(species_list) >= 1000:
                Species.objects.bulk_create(species_list)
                species_list = []
        
        # Вставляем оставшиеся записи
        if species_list:
            Species.objects.bulk_create(species_list)

def delete_species_data(apps, schema_editor):
    # Функция отката миграции (удаление всех данных)
    Species = apps.get_model('bio', 'Species')
    Species.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('bio', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_species_from_csv, delete_species_data),
    ] 