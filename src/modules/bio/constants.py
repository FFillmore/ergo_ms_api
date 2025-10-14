"""
Константы для модуля биоразнообразия
"""

# Словарь шкал с полями модели и отображаемыми именами
SCALES_DICT = {
    'ellenberg': [
        ('eLight', 'Light'), 
        ('eTemperature', 'Temperature'), 
        ('eContinentality', 'Continentality'), 
        ('eMoisture', 'Moisture'), 
        ('eReaction', 'Reaction'), 
        ('eNutrient', 'Nutrient')
    ],
    'landolt': [
        ('lLight', 'Light'), 
        ('lTemperature', 'Temperature'), 
        ('lContinentality', 'Continentality'), 
        ('lMoisture', 'Moisture'), 
        ('lReaction', 'Reaction'), 
        ('lNutrient', 'Nutrient'), 
        ('lHumus', 'Humus'), 
        ('lDispersion', 'Dispersion')
    ],
    'tsyganov': [
        ('tm1', 'TM1'), ('tm2', 'TM2'), 
        ('kn1', 'KN1'), ('kn2', 'KN2'), 
        ('om1', 'OM1'), ('om2', 'OM2'), 
        ('cr1', 'CR1'), ('cr2', 'CR2'), 
        ('hd1', 'HD1'), ('hd2', 'HD2'), 
        ('tr1', 'TR1'), ('tr2', 'TR2'), 
        ('nt1', 'NT1'), ('nt2', 'NT2'), 
        ('rc1', 'RC1'), ('rc2', 'RC2'), 
        ('lc1', 'LC1'), ('lc2', 'LC2'), 
        ('fh1', 'FH1'), ('fh2', 'FH2')
    ],
}

# Словарь для преобразования символов обилия в числовые значения
ABUNDANCE_SYMBOLS_TO_VALUES = {
    'r': 0.001,
    '+': 0.01,
    '1': 0.05,
    '2': 0.15,
    '3': 0.375,
    '4': 0.625,
    '5': 0.875
}

# Названия типов спектра
SPECTRUM_TITLE_MAP = {
    'raunkiaer': 'Спектр жизненных форм по К. Раункиеру',
    'serebryakov': 'Спектр жизненных форм по И.Г. Серебрякову',
    'ecobiomorphs': 'Спектр экобиоморф',
    'geoelements': 'Спектр геоэлементов и полизональных групп',
    'ta': 'Спектр типов ареала'
}

# Метки для осей графиков
SPECTRUM_LABEL_MAP = {
    'raunkiaer': 'Жизненная форма',
    'serebryakov': 'Жизненная форма',
    'ecobiomorphs': 'Экобиоморфа',
    'geoelements': 'Геоэлемент',
    'ta': 'Тип ареала'
}

# Поддерживаемые типы спектров
SUPPORTED_SPECTRUM_TYPES = ['raunkiaer', 'serebryakov', 'ecobiomorphs', 'geoelements', 'ta'] 