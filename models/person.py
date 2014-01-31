from django.db import models

from document import Document
from documentary import Documentary
import re


class Person(models.Model):
    class Meta:
        app_label = 'gedgo'
        verbose_name_plural = 'People'
    pointer = models.CharField(max_length=10, primary_key=True)
    gedcom = models.ForeignKey('Gedcom')

    # Name
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    prefix = models.CharField(max_length=255)
    suffix = models.CharField(max_length=255)

    # Details
    education = models.TextField(null=True)
    religion = models.CharField(max_length=255, null=True, blank=True)

    # Life dates
    birth = models.ForeignKey(
        'Event',
        related_name='person_birth',
        null=True,
        blank=True
    )
    death = models.ForeignKey(
        'Event',
        related_name='person_death',
        null=True,
        blank=True
    )

    # Family
    child_family = models.ForeignKey(
        'Family',
        related_name='person_child_family',
        null=True,
        blank=True
    )
    spousal_families = models.ManyToManyField(
        'Family',
        related_name='person_spousal_families'
    )

    # Notes
    notes = models.ManyToManyField('Note', null=True)

    # Profile
    profile = models.ManyToManyField('Document', null=True, blank=True)

    def __unicode__(self):
        return '%s, %s (%s)' % (self.last_name, self.first_name, self.pointer)

    @property
    def photos(self):
        return Document.objects.filter(tagged_people=self, kind='PHOTO')

    @property
    def documents(self):
        docs = Document.objects.filter(tagged_people=self)
        return [d for d in docs if d.kind not in ['PHOTO', 'DOCUV']]

    @property
    def documentaries(self):
        return Documentary.objects.filter(tagged_people=self)

    @property
    def key_photo(self):
        if self.profile.exists():
            return self.profile.first()

        photos = Document.objects.filter(tagged_people=self, kind='PHOTO')

        if photos:
            name_filtered = [
                p for p in photos if not
                BLOCK_TAGS_RE.findall(p.docfile.name)
            ]
            if name_filtered:
                return name_filtered[len(name_filtered) - 1]
            else:
                return photos[len(photos) - 1]

    @property
    def year_range(self):
        if self.birth_year == '?' and self.death_year == '?':
            return 'unknown'

        return '%s%d - %s%d' % (
            '~' if self.birth and self.birth.date_approxQ else '',
            self.birth_year,
            '~' if self.death and self.death.date_approxQ else '',
            self.death_year
        )

    @property
    def birth_year(self):
        if not self.birth or not self.birth.date:
            return '?'
        return self.birth.date.year

    @property
    def death_year(self):
        if not self.death or not self.death.date:
            return '?'
        return self.death.date.year

    @property
    def full_name(self):
        return ' '.join(
            [
                self.prefix or '',
                self.first_name,
                self.last_name,
                ('' if self.suffix == '' or self.suffix[0] == ',' else ' '),
                self.suffix
            ]
        ).strip(' ')

    @property
    def education_delimited(self):
        if self.education:
            return '\n'.join(self.education.strip(';').split(';'))
        else:
            return ''

# Keywords to filter out document-type photos in preference of portraits.
BLOCK_TAGS_RE = re.compile(
    "(?i)(?:death|birth|masscard|census|burial|tax|obit|cemet(?:a|e)ry|"
    "(?:grave|head)stone|baptism|baptcert|baptrec|burrec|lists?\\b|military|"
    "record|letter|\\bwill\\b|hsdip|road|street|directory)"
)
