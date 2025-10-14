from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    ChoiceField,
    IntegerField,
    ValidationError,
    Serializer,
)

from src.modules.bio.geobotany.models import Species, Site, Description


class SpeciesSerializer(ModelSerializer):
    class Meta:
        model = Species
        fields = '__all__'
        read_only_fields = ['species_id']


class SiteSerializer(ModelSerializer):
    zone_type = ChoiceField(choices=Site._meta.get_field('zone_type').choices, help_text="Тип местности")
    site_number = IntegerField(help_text="Номер площадки в рамках пользователя (уникален в связке с zone_type)")

    class Meta:
        model = Site
        fields = '__all__'
        read_only_fields = ['id', 'user']

    def validate(self, data):
        user = self.context['request'].user
        site_number = data.get('site_number')
        zone_type = data.get('zone_type')

        if self.instance is None:
            if Site.objects.filter(user=user, site_number=site_number, zone_type=zone_type).exists():
                raise ValidationError({"site_number": f"Такая площадка уже существует"})
        else:
            if Site.objects.filter(user=user, site_number=site_number, zone_type=zone_type).exclude(id=self.instance.id).exists():
                raise ValidationError({"site_number": f"Такая площадка уже существует"})

        return data


class DescriptionSerializer(ModelSerializer):
    title = CharField(source='species.title', read_only=True)
    author = CharField(source='species.author', read_only=True)
    site_number = IntegerField(source='site.site_number', read_only=True)
    zone_type = CharField(source='site.zone_type', read_only=True)
    species_id = IntegerField(source='species.species_id', read_only=True)

    class Meta:
        model = Description
        fields = ['id', 'species_id', 'tier', 'abundance', 'title', 'author', 'site_number', 'zone_type']
        read_only_fields = ['id', 'species_id', 'title', 'author', 'site_number', 'zone_type']


class DescriptionCreateSerializer(Serializer):
    title = CharField(max_length=255, help_text="Название вида")
    author = CharField(max_length=255, help_text="Автор вида")
    tier = ChoiceField(choices=Description._meta.get_field('tier').choices, help_text="Ярус растения (A, B, C, D или пусто)")
    abundance = ChoiceField(choices=Description._meta.get_field('abundance').choices, help_text="Балл обилия растения (r, +, 1-5)")

    def validate(self, data):
        title = data.get('title')
        author = data.get('author')
        try:
            species = Species.objects.get(title=title, author=author)
        except Species.DoesNotExist:
            raise ValidationError({"species": f"Вид с названием '{title}' и автором '{author}' не найден"})
        data['species'] = species
        return data



