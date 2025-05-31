from django.shortcuts import render, redirect
from .decorators import supervisor_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate,get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, UserIssueForm, SuggestionForm
from django.contrib import messages
from django.utils import timezone
import json 
from .nlp_utils import extract_keywords, extract_keywords_and_groups 
from .models import VoteTopic, Vote, AnonymousMessage, Suggestion, User, UserIssue
from .utils import detect_emergency
from django.db.models import Count
# import pprint

# Register Users
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')
        
        if password != confirm:
            return render(request, 'core/register.html', {'error': 'Passwords do not match'})

        if get_user_model().objects.filter(username=username).exists():
            return render(request, 'core/register.html', {'error': 'Username already exists'})

        user = get_user_model().objects.create_user(username=username, password=password, role='whistleblower')
        return redirect('login')

    return render(request, 'core/register.html')

# Login
def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Redirect based on role
            if user.role == 'supervisor':
                return redirect('supervisor_home')
            else:
                return redirect('user_home')  # default to user

    else:
        form = AuthenticationForm()

    return render(request, 'core/login.html', {'form': form})

@login_required
def user_home(request):
    form = UserIssueForm()
    user_issues = UserIssue.objects.filter(user=request.user).order_by('-submitted_at')

    if request.method == 'POST':
        form = UserIssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.user = request.user

            # Use NLP to extract keywords
            keywords = extract_keywords(issue.message)
            issue.core_words = keywords

            # Check for similar issues by the same user
            same_issues = Issue.objects.filter(user=request.user, category=issue.category, core_words__overlap=keywords)
            if same_issues.count() > 1:
                issue.is_priority = True

            issue.save()
            return redirect('user_home')

    return render(request, 'core/user_home.html', {'form': form, 'issues': user_issues})

@login_required
def raise_issue(request):
    if request.method == 'POST':
        form = UserIssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            # Run emergency detection on title + description
            combined_text = issue.title + ' ' + issue.description
            issue.is_emergency = detect_emergency(combined_text)
            issue.save()
            return redirect('user_home')
    else:
        form = UserIssueForm()
    return render(request, 'core/raise_issue.html', {'form': form})

@login_required
@supervisor_required
def supervisor_home(request):
    # Voting results aggregation (example)
    vote_results = Vote.objects.values('topic__question', 'choice').annotate(total=Count('id')).order_by('topic__question')

    # Suggestions list (last 20)
    suggestions = Suggestion.objects.order_by('-submitted_at')[:20]
    print("=== DEBUG: Total Suggestions ===", Suggestion.objects.count())
    for s in Suggestion.objects.all():
        print(f"- {s.message} | submitted_at={s.submitted_at}")


    # Issues list (last 20)
    issues = UserIssue.objects.order_by('-submitted_at')[:20]

    # Extract texts from issues for NLP processing
    issue_texts = [issue.description for issue in issues]

    # Use NLP utility to get chart data and grouped messages
    issue_chart_data, keyword_to_messages = extract_keywords_and_groups(issue_texts, top_n_keywords=6)

    context = {
        'vote_results': vote_results,
        'suggestions': suggestions,
        'issues': issues,
        # JSON dumps for JavaScript in template
        'issue_chart_data': json.dumps(issue_chart_data),
        'keyword_to_messages': json.dumps(keyword_to_messages),
    }
    return render(request, 'core/supervisor_home.html', context)


def home(request):
    return render(request, 'core/home.html')

def public_voting(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    # Fetch active & not expired topics
    topics = VoteTopic.objects.filter(is_active=True)
    topics = [t for t in topics if not t.is_expired()]

    if not topics:
        return render(request, 'core/no_topic.html')

    topic_id = request.GET.get('topic')
    if topic_id:
        try:
            topic = VoteTopic.objects.get(id=topic_id, is_active=True)
            if topic.is_expired():
                messages.error(request, "Selected topic has expired.")
                return redirect('public_voting')
        except VoteTopic.DoesNotExist:
            messages.error(request, "Selected topic does not exist.")
            return redirect('public_voting')
    else:
        topic = topics[0]

    already_voted = Vote.objects.filter(topic=topic, session_key=session_key).exists()

    if request.method == 'POST':
        if already_voted:
            messages.error(request, "You have already voted on this topic.")
        else:
            choice = request.POST.get('choice')
            justification = request.POST.get('justification', '').strip()  # Capture the justification
            valid_choices = topic.get_choices()

            if choice and choice in valid_choices:
                # Save the vote with justification
                Vote.objects.create(topic=topic, choice=choice, session_key=session_key, justification=justification)
                messages.success(request, "Vote submitted! Thank you for voting.")
                return redirect(f'/public/?topic={topic.id}&voted=1')
            else:
                messages.error(request, "Invalid choice selected.")

    # After voting, show vote results summary for this topic to the voter (optional)
    show_results = request.GET.get('voted') == '1'
    votes = Vote.objects.filter(topic=topic)
    total_votes = votes.count()
    results = {}
    chart_labels = []  # Initialize an empty list for chart labels
    chart_data = []    # Initialize an empty list for chart data

    if total_votes > 0:
        for choice in topic.get_choices():
            count = votes.filter(choice=choice).count()
            percent = round((count / total_votes) * 100, 1)
            results[choice] = {'count': count, 'percent': percent}
            chart_labels.append(choice)  # Add choice to chart labels
            chart_data.append(count)     # Add count to chart data

    # Convert the chart labels and data to JSON for frontend use
    chart_labels_json = json.dumps(chart_labels)
    chart_data_json = json.dumps(chart_data)

    return render(request, 'core/public_voting.html', {
        'topics': topics,
        'topic': topic,
        'already_voted': already_voted,
        'show_results': show_results,
        'results': results,
        'chart_labels': chart_labels_json,  # Pass chart labels to template
        'chart_data': chart_data_json,      # Pass chart data to template
    })

def anonymous_suggestion(request):
    if request.method == 'POST':
        form = SuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.session_key = request.session.session_key or 'anonymous'
            suggestion.save()
            messages.success(request, "Message sent anonymously!")
            return redirect('anonymous_suggestion')
    else:
        form = SuggestionForm()

    suggestions = Suggestion.objects.order_by('-submitted_at')
    return render(request, 'core/anonymous_suggestion.html', {
        'form': form,
        'suggestions': suggestions,
    })

def anonymous_entry(request):
    return render(request, 'core/anonymous_entry.html')

def public_mode(request):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    topic = VoteTopic.objects.filter(is_active=True).last()
    already_voted = Vote.objects.filter(topic=topic, session_key=session_key).exists() if topic else False

    if request.method == 'POST':
        if 'vote_submit' in request.POST:
            if topic and not already_voted:
                choice = request.POST.get('choice')
                if choice:
                    Vote.objects.create(topic=topic, choice=choice, session_key=session_key)
                    messages.success(request, "Your vote has been recorded.")
                    return redirect('public_mode')
                else:
                    messages.error(request, "Please select a choice.")
            else:
                messages.error(request, "You have already voted or topic is missing.")

        elif 'suggestion_submit' in request.POST:
            suggestion_msg = request.POST.get('suggestion')
            suggestion_topic_id = request.POST.get('suggestion_topic')
            suggestion_topic = VoteTopic.objects.filter(id=suggestion_topic_id).first()
            if suggestion_msg:
                Suggestion.objects.create(
                    topic=suggestion_topic,
                    message=suggestion_msg,
                    session_key=session_key
                )
                messages.success(request, "Suggestion sent successfully.")
                return redirect('public_mode')

    topics = VoteTopic.objects.filter(is_active=True)

    return render(request, 'core/public_mode.html', {
        'current_topic': topic,
        'already_voted': already_voted,
        'topics': topics,
    })





#Supervisor functionalities

# views.py
from django.forms import formset_factory
from django.shortcuts import render, redirect
from .forms import VoteTopicForm, ChoiceForm
from .models import VoteTopic, Choice
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import supervisor_required

@login_required
@supervisor_required
def manage_vote_topics(request):
    ChoiceFormSet = formset_factory(ChoiceForm, extra=2)

    if request.method == 'POST':
        topic_form = VoteTopicForm(request.POST)
        formset = ChoiceFormSet(request.POST)

        if topic_form.is_valid() and formset.is_valid():
            topic = topic_form.save()
            for form in formset:
                if form.cleaned_data.get('text'):
                    Choice.objects.create(topic=topic, text=form.cleaned_data['text'])
            messages.success(request, "Vote topic and choices added successfully.")
            return redirect('manage_vote_topics')
    else:
        topic_form = VoteTopicForm()
        formset = ChoiceFormSet()

    all_topics = VoteTopic.objects.prefetch_related('choices').order_by('-created_at')

    return render(request, 'core/manage_vote_topics.html', {
        'topic_form': topic_form,
        'formset': formset,
        'topics': all_topics,
    })
