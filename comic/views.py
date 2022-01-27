from django.http import Http404

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
# from django.views.decorators.http import require_POST
from django.core.signing import TimestampSigner, BadSignature
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.cache import add_never_cache_headers
from django.views.decorators.gzip import gzip_page

from .models import ComicPanel, SecretPanel, Page
# from anthrofractal.config import settings
from django.utils import timezone

from thefuzz import process, fuzz

import uuid


def get_session_last_number(request):
    last_number = request.session.get('last_panel', default=1)
    last_number = min(last_number, ComicPanel.last_number())
    return last_number


@gzip_page
def index(request):
    last_number = get_session_last_number(request)
    return redirect('comic-panel', number=last_number)


@gzip_page
def archive(request):
    panels = ComicPanel.objects.filter(published__lte=timezone.now())
    last_number = get_session_last_number(request)
    last_panel = get_object_or_404(ComicPanel, number=last_number)  # should never error out tbh
    
    context = {'panels': panels, 'last_panel': last_panel}
    return render(request, 'comic/archive.html', context)


@gzip_page
def howto(request):
    context = {}
    return render(request, 'comic/howto.html', context)


@gzip_page
def panel(request, number: int):
    if request.user.is_staff:  # show unpublished panels for admins
        panel = get_object_or_404(ComicPanel, number=number)
        cache = False
    else:
        panel = get_object_or_404(ComicPanel, number=number, published__lte=timezone.now())
        cache = True
    
    request.session['last_panel'] = panel.number
    context = {'panel': panel}
    response = render(request, 'comic/viewer.html', context)
    if not cache:
        add_never_cache_headers(response)
    return response


def secret(request, u_id: uuid.UUID):
    panel = get_object_or_404(SecretPanel, id=u_id)
    context = {'panel': panel}
    response = render(request, 'comic/secret.html', context)
    add_never_cache_headers(response)
    return response


@staff_member_required()
def secret_preview(request, u_id: uuid.UUID):
    return secret(request, u_id)


def secret_signed(request, signature):
    signer = TimestampSigner(salt=request.session.session_key)
    try:
        unsigned = signer.unsign(signature, max_age=60*15)  # 15 minutes
    except BadSignature:
        raise Http404("No.")

    u_id = uuid.UUID(unsigned)
    return secret(request, u_id)


@gzip_page
def tag(request, slug: str):
    tag = get_object_or_404(ComicPanel.tags.tag_model, slug=slug)
    panels = ComicPanel.objects.filter(tags=tag, published__lte=timezone.now())
    if len(panels) == 1:
        panel = panels[0]
        return redirect('comic-panel', number=panel.number)

    context = {'panels': panels,
               'query': f'tag \'{tag.name}\'',
               }
    return render(request, 'comic/gallery.html', context)


def to_search_dict(results, obj_type):
    return [dict(text=text, score=score, obj=obj, type=obj_type) for text, score, obj in results]


def search_engine(query, score_cutoff=80, scorer=fuzz.WRatio):
    # panels
    panels = ComicPanel.objects.filter(published__lte=timezone.now())
    panel_title_dict = {panel: panel.title for panel in panels}
    filtered_titles = process.extractBests(query, panel_title_dict, score_cutoff=score_cutoff, scorer=scorer)

    panel_alt_dict = {panel: panel.alt for panel in panels}
    filtered_alts = process.extractBests(query, panel_alt_dict, score_cutoff=score_cutoff, scorer=scorer)

    filtered_panels = to_search_dict(filtered_titles + filtered_alts, 'panel')

    # pages
    pages = panels.order_by('page').values_list('page', flat=True).distinct()
    pages = Page.objects.filter(pk__in=pages)
    pages_title_dict = {page: page.title for page in pages}
    filtered_pages = process.extractBests(query, pages_title_dict, score_cutoff=score_cutoff, scorer=scorer)
    filtered_pages = to_search_dict(filtered_pages, 'page')

    # tags
    tags = panels.order_by('tags').values_list('tags', flat=True).distinct()
    tags = ComicPanel.tags.tag_model.objects.filter(pk__in=tags)

    tag_dict = {tag: tag.name for tag in tags}
    filtered_tags = process.extractBests(query, tag_dict, score_cutoff=score_cutoff, scorer=scorer)

    filtered_tags = to_search_dict(filtered_tags, 'tag')

    suggestions = filtered_tags + filtered_panels + filtered_pages
    # sort by score
    suggestions.sort(key=lambda x: x['score'], reverse=True)

    # ensure only unique objects are shown (if there are several matches for the same object)
    suggestions = list(reversed({value['obj']: value for value in reversed(suggestions)}.values()))

    return suggestions


def search_secret(query, score_cutoff=80, scorer=fuzz.ratio):
    """Returns SecretPanel obj or None depending on match"""
    # score_cutoff = 85 for stricter
    secrets = SecretPanel.objects.all()

    secrets_dict = {secrets: secrets.key_phrase for secrets in secrets}
    result = process.extractOne(query, secrets_dict, score_cutoff=score_cutoff, scorer=scorer)
    # string key, score, object
    # print(query, result)
    return result[2] if result is not None else None


def live_search(request):
    query = request.GET.get('q')
    suggestions = search_engine(query)

    context = {'suggestions': suggestions}
    return render(request, 'comic/suggestions.html', context)


@csrf_protect
def search(request):
    if request.method == 'POST':
        query = request.POST.get('q')
        secret = search_secret(query)
        if secret is not None:
            signer = TimestampSigner(salt=request.session.session_key)
            signature = signer.sign(secret.id)
            return redirect('comic-secret', signature=signature)

        response = redirect('comic-search-request')
        response['Location'] += f'?q={query}'
        return response

    if request.method == 'GET':
        query = request.GET.get('q')
        suggestions = search_engine(query)

        to_show = list()
        for suggestion in suggestions:
            suggestion_type = suggestion['type']
            if suggestion_type == 'tag':
                tag = suggestion['obj']
                for panel in ComicPanel.objects.filter(tags=tag.pk):
                    if panel not in to_show:
                        to_show.append(panel)
            elif suggestion_type == 'panel':
                panel = suggestion['obj']
                if panel not in to_show:
                    to_show.append(panel)
            elif suggestion_type == 'page':
                page = suggestion['obj']
                panel = page.panels.order_by('number').first()
                if panel not in to_show:
                    to_show.append(panel)

        results_num = len(to_show)
        # print(suggestions)
        # print(to_show)
        context = {'panels': to_show,
                   'query': query,
                   'results_num': results_num,
                   }
        return render(request, 'comic/gallery.html', context)

    raise Http404("??????")

