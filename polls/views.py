from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views import generic
from polls.models import Poll, Choice
from django.utils import timezone
from django.db.models import Count


def filter_polls():
    """
    Excludes polls with less than 2 choices or future pub_date.
    """
    p = Poll.objects.annotate(num_choices=Count('choice'))
    return p.filter(pub_date__lte = timezone.now(), num_choices__gte = 2)


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_poll_list'

    def get_queryset(self):
        return filter_polls().order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    template_name = 'polls/detail.html'

    def get_queryset(self):
        return filter_polls()


def vote(request, poll_id):
    p = get_object_or_404(filter_polls().filter(pk = poll_id))
    try:
        selected_choice = p.choice_set.get(pk = request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html',
            {'poll': p, 'error_message': "You didn't select a choice",}
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
    return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))


class ResultsView(generic.DetailView):
    template_name = 'polls/results.html'

    def get_queryset(self):
        return filter_polls()