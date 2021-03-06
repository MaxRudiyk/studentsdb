# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.views.generic import UpdateView, CreateView, DeleteView
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.core.urlresolvers import reverse

from ..models import Group, Student
from ..forms import GroupAddForm, GroupUpdateForm
from ..util import paginate
# Create your views here.

# Views for Groups

class GroupList(TemplateView):
    template_name = 'students/groups_list.html'

    def get_context_data(self, **kwargs):
        context = super(GroupList, self).get_context_data(**kwargs)

        groups = Group.objects.all()

        # Order groups list
        order_by = self.request.GET.get('order_by', '') # Витягуємо параметр order_by з GET словника
        reverse = self.request.GET.get('reverse', '') # Витягуємо параметр reverse з GET словника

        if order_by in ('title', 'leader', 'id'):
            groups = groups.order_by(order_by)
            if reverse == '1':
                groups = groups.reverse()

        context = paginate(groups, 3, self.request, context, var_name='groups_list')

        return context


class GroupAddView(CreateView):
    template_name = 'students/universal_form.html'
    form_class = GroupAddForm
    model = Group

    def get_success_url(self):
        return reverse('groups')

    def post(self, request, *args, **kwargs):

        if request.POST.get('cancel_button'):
            messages.warning(request, 'Додавання групи відмінено')
            return HttpResponseRedirect(reverse('groups'))
        else:
            messages.success(request, 'Групу успішно збережено')
            return super(GroupAddView, self).post(request, *args, **kwargs)

class GroupUpdateView(UpdateView):
    template_name = 'students/universal_form.html'
    form_class = GroupUpdateForm
    model = Group

    def get_success_url(self):
        return reverse('groups')

    def post(self, request, *args, **kwargs):

        if request.POST.get('cancel_button'):
            messages.warning(request, 'Редагування групи відмінено')
            return HttpResponseRedirect(reverse('groups'))
        else:
            messages.success(request, 'Групу успішно збережено')
            return super(GroupUpdateView, self).post(request, *args, **kwargs)




class GroupDeleteView(DeleteView):
    model = Group
    template_name = 'students/confirm_delete.html'
    context_object_name = 'context'

    def get_context_data(self, **kwargs):
        context = super(GroupDeleteView, self).get_context_data(**kwargs)
        context['question'] = u'Ви дійсно бажаєте видалити групу'
        context['title'] = u'Видалити групу'
        context['context_url'] = 'groups_delete'
        context['context_id'] = self.kwargs['pk']
        return context

    def get_success_url(self):
        return reverse('groups')

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel_button'):
            messages.warning(request, 'Видалення групи відмінено')
            return HttpResponseRedirect(reverse('groups'))
        else:

            if Student.objects.filter(student_group__pk=self.kwargs['pk']):
                messages.error(self.request, "Групу неможливо видалити коли в ній присутній хоча б один студент")
                return HttpResponseRedirect(reverse('groups'))
            else:
                messages.success(self.request, "Групу успішно видалено")
                return super(GroupDeleteView, self).post(request, *args, **kwargs)

def groups_delete(request, gid):

    group = Group.objects.get(pk=gid)

    if request.POST.get('cancel_button'):
        messages.warning(request, 'Видалення групи відмінено')
        return HttpResponseRedirect(reverse('groups'))

    elif request.POST.get('delete_button'):
        
        if Student.objects.filter(student_group__pk=gid):
            messages.error(request, "Групу неможливо видалити коли в ній присутній хоча б один студент")
            return HttpResponseRedirect(reverse('groups'))
        else:

            try:
                group.delete()
                messages.success(request, "Групу успішно видалено")
            except Exception:
                messages.warning(request, 'Виникла непередбачувана помилка')
                
        return HttpResponseRedirect(reverse('groups'))

    return render(request, 'students/groups_confirm_delete.html', {'group': group})
