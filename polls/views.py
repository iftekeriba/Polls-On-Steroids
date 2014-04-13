from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views import generic
from polls.models import Poll, Choice
from django.utils import timezone
from django.db.models import Count


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_poll_list'

    def get_queryset(self):
        p = Poll.objects.annotate(num_choices=Count('choice'))
        return p.filter(
            pub_date__lte = timezone.now(), num_choices__gte = 2
            ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Poll
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any polls that aren't published yet.
        """
        return Poll.objects.filter(pub_date__lte = timezone.now())


def vote(request, poll_id):
    p = get_object_or_404(Poll.objects.filter(pub_date__lte = timezone.now()),
                          pk = poll_id)
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
    model = Poll
    template_name = 'polls/results.html'

    def get_queryset(self):
        return Poll.objects.filter(pub_date__lte = timezone.now())