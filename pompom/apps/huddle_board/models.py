import random

from ckeditor.fields import RichTextField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel, TitleDescriptionModel
from ordered_model.models import OrderedModel

from .utils import truncate_string


MAX_CARDS_DISPLAYED = 3


class Card(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('title'))
    companion_image = models.ImageField(upload_to='companion_images/', blank=True, null=True,
                                        verbose_name=_('companion image'))

    def __str__(self):
        return self.title


class CardSection(OrderedModel):
    title = models.CharField(blank=True, null=True, max_length=255, verbose_name=_('title'))
    contents = RichTextField(blank=True, null=True, verbose_name=_('contents'))
    card = models.ForeignKey(Card, related_name='sections', verbose_name=_('card'))
    is_gradable = models.BooleanField(verbose_name=_('is gradable'))

    order_with_respect_to = 'card'

    def __str__(self):
        return self.title or "(no title)"


class GradedCardSection:

    def __init__(self, card_section, observation):
        self.section = card_section
        self.grade = self.grade_section(observation)

    def grade_section(self, observation):
        if not observation:
            return None
        try:
            answer = observation.answers.get(card_section=self.section)
        except Answer.DoesNotExist:
            return None
        return answer.grade


class GradedCard:

    def __init__(self, observation):
        self.card = observation.card
        self.graded_sections = [GradedCardSection(section, observation) for section in self.card.sections.all()]
        self.grade = self.grade_card()
        self.datetime = observation.created

    def grade_card(self):
        section_grades = {section.grade for section in self.graded_sections}
        if False in section_grades:
            return False
        if True in section_grades:
            return True
        return None


class Deck(TitleDescriptionModel):
    cards = models.ManyToManyField(Card, blank=True, related_name='decks', verbose_name=_('cards'))

    def __str__(self):
        return self.title


class Board(TitleDescriptionModel):
    deck = models.ForeignKey(Deck, blank=True, null=True, verbose_name=_('deck'))

    def __str__(self):
        return self.title

    class DeckException(Exception):
        pass

    def draw_card(self):
        self.validate_non_empty_deck()
        deck_size = self.deck.cards.count()
        random_index = random.randrange(deck_size)
        return self.deck.cards.all()[random_index]

    def validate_non_empty_deck(self):
        if not self.deck:
            raise self.DeckException("Cannot draw a card; board has no deck assigned.")
        if not self.deck.cards.exists():
            raise self.DeckException("Cannot draw a card; assigned deck has no cards.")

    def latest_observations(self):
        return self.observations.all()[:MAX_CARDS_DISPLAYED]

    def latest_cards(self):
        observations = self.latest_observations()
        return [observation.card for observation in observations]

    def latest_graded_cards(self):
        observations = self.latest_observations()
        return [GradedCard(observation) for observation in observations]


class Observation(TimeStampedModel):
    board = models.ForeignKey(Board, related_name='observations', verbose_name=_('board'))
    card = models.ForeignKey(Card, related_name='observations', verbose_name=_('card'))


class Answer(models.Model):
    GRADES = ((True, 'Pass'), (False, 'Fallout'), (None, 'N/A'))

    observation = models.ForeignKey(Observation, related_name='answers', verbose_name=_('observation'))
    card_section = models.ForeignKey(CardSection, related_name='answers', verbose_name=_('card section'))
    grade = models.NullBooleanField(choices=GRADES)

    def __str__(self):
        return ', '.join([str(self.observation), str(self.card_section), str(self.grade)])


class CardNote(TimeStampedModel):
    contents = models.TextField(verbose_name=_('contents'))
    board = models.ForeignKey(Board, related_name='notes', verbose_name=_('board'))
    card = models.ForeignKey(Card, related_name='notes', verbose_name=_('card'))

    def __str__(self):
        return truncate_string(self.contents)
