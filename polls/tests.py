import datetime
from django.test import TestCase
from django.utils import timezone
from polls.models import Poll
from django.core.urlresolvers import reverse


class PollMethodTests(TestCase):

    def test_was_published_recently_with_future_poll(self):
        """
        was_published_recently() should return False for polls whose
        pub_date is in the future
        """
        future_poll = Poll(pub_date=timezone.now() + datetime.timedelta(days=30))
        self.assertEqual(future_poll.was_published_recently(), False)

    def test_was_published_recently_with_old_poll(self):
        """
        was_published_recently() should return False for polls whose pub_date
        is older than 1 day
        """
        old_poll = Poll(pub_date=timezone.now() - datetime.timedelta(days=30))
        self.assertEqual(old_poll.was_published_recently(), False)

    def test_was_published_recently_with_recent_poll(self):
        """
        was_published_recently() should return True for polls whose pub_date
        is within the last day
        """
        recent_poll = Poll(pub_date=timezone.now() - datetime.timedelta(hours=1))
        self.assertEqual(recent_poll.was_published_recently(), True)


def create_poll(question, days, num_choices):
    """
    Creates a poll with the given 'question' published with an offset
    of 'days' with respect to now and 'num_choices' available choices.
    """
    p = Poll.objects.create(question=question,
        pub_date = timezone.now() + datetime.timedelta(days=days))
    for i in range (0, num_choices):
        p.choice_set.create(choice_text=str(i), votes=0)
    return p


class PollIndexViewTests(TestCase):
    """
    Only past polls with 2 or more choices must be shown.
    If there are no polls, or none of them satisfy these conditions,
    an appropriate message should be displayed.
    """
    def test_index_view_with_no_polls(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_with_a_past_poll_with_2_choices(self):
        create_poll("Past poll.", days=-30, num_choices=2)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_poll_list'],
            ['<Poll: Past poll.>'])

    def test_index_with_a_past_poll_with_0_choices(self):
        create_poll("Past poll.", days=-30, num_choices=0)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.", status_code=200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_a_future_poll_with_2_choices(self):
        create_poll(question="Future poll.", days=30, num_choices=2)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.", status_code=200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_a_future_poll_with_0_choices(self):
        create_poll(question="Future poll.", days=30, num_choices=0)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.", status_code=200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_future_poll_and_past_poll_with_2_choices_each(self):
        create_poll(question="Past poll.", days=-30, num_choices=2)
        create_poll(question="Future poll.", days=30, num_choices=2)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
            ['<Poll: Past poll.>']
        )

    def test_index_view_with_2_past_polls_with_0_and_2_choices(self):
        create_poll(question="Past poll with 0 choices.", days=-30, num_choices=0)
        create_poll(question="Past poll with 2 choices.", days=-30, num_choices=2)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
            ['<Poll: Past poll with 2 choices.>']
        )

    def test_index_view_with_two_past_polls_with_2_choices_each(self):
        create_poll(question="Past poll 1.", days=-30, num_choices=2)
        create_poll(question="Past poll 2.", days=-5, num_choices=2)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
             ['<Poll: Past poll 2.>', '<Poll: Past poll 1.>']
        )


class DetailViewTests(TestCase):
    """
    Only a past poll with 2 or more choices will be accessible.
    """
    def test_detail_view_with_a_past_poll_with_2_choices(self):
        past_poll = create_poll(question='Past Poll.', days=-5, num_choices=2)
        response = self.client.get(reverse('polls:detail', args=(past_poll.id,)))
        self.assertContains(response, past_poll.question, status_code=200)

    def test_detail_view_with_a_past_poll_with_0_choices(self):
        future_poll = create_poll(question='Past poll.', days=5, num_choices=0)
        response = self.client.get(reverse('polls:detail', args=(future_poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_future_poll_with_2_choices(self):
        future_poll = create_poll(question='Future poll.', days=5, num_choices=2)
        response = self.client.get(reverse('polls:detail', args=(future_poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_future_poll_with_0_choices(self):
        future_poll = create_poll(question='Past poll.', days=5, num_choices=0)
        response = self.client.get(reverse('polls:detail', args=(future_poll.id,)))
        self.assertEqual(response.status_code, 404)


class ResultsViewTests(TestCase):
    """
    Only a past poll with 2 or more choices will be accessible.
    """
    def test_results_view_with_a_past_poll_with_2_choices(self):
        past_poll = create_poll(question='Past Poll.', days=-5, num_choices=2)
        response = self.client.get(reverse('polls:results', args=(past_poll.id,)))
        self.assertContains(response, past_poll.question, status_code=200)

    def test_results_view_with_a_past_poll_with_0_choices(self):
        future_poll = create_poll(question='Past poll.', days=5, num_choices=0)
        response = self.client.get(reverse('polls:results', args=(future_poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_future_poll_with_2_choices(self):
        future_poll = create_poll(question='Future poll.', days=5, num_choices=2)
        response = self.client.get(reverse('polls:results', args=(future_poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_future_poll_with_0_choices(self):
        future_poll = create_poll(question='Past poll.', days=5, num_choices=0)
        response = self.client.get(reverse('polls:results', args=(future_poll.id,)))
        self.assertEqual(response.status_code, 404)


class VoteViewTests(TestCase):
    """
    Only a past poll with 2 or more choices will be accessible.
    """
    def test_vote_view_with_a_past_poll_with_2_choices(self):
        past_poll = create_poll(question='Past Poll.', days=-5, num_choices=2)
        response = self.client.get(reverse('polls:vote', args=(past_poll.id,)))
        self.assertContains(response, past_poll.question, status_code=200)

    def test_vote_view_with_a_past_poll_with_0_choices(self):
        future_poll = create_poll(question='Past poll.', days=5, num_choices=0)
        response = self.client.get(reverse('polls:vote', args=(future_poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_vote_view_with_a_future_poll_with_2_choices(self):
        future_poll = create_poll(question='Future poll.', days=5, num_choices=2)
        response = self.client.get(reverse('polls:vote', args=(future_poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_vote_view_with_a_future_poll_with_0_choices(self):
        future_poll = create_poll(question='Past poll.', days=5, num_choices=0)
        response = self.client.get(reverse('polls:vote', args=(future_poll.id,)))
        self.assertEqual(response.status_code, 404)