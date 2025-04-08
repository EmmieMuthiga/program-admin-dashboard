from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Post, Campaign
from forms import PostForm, CampaignForm
from app import db
from utils import save_file
from datetime import datetime

marketing_bp = Blueprint('marketing', __name__, url_prefix='/marketing')

@marketing_bp.route('/scheduler')
@login_required
def scheduler():
    posts = Post.query.order_by(Post.scheduled_date.desc()).all()
    form = PostForm()
    return render_template('marketing/scheduler.html', posts=posts, form=form, title='Post Scheduler')

@marketing_bp.route('/posts/create', methods=['POST'])
@login_required
def create_post():
    form = PostForm()
    
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            scheduled_date=form.scheduled_date.data,
            platform=form.platform.data,
            status=form.status.data,
            created_by=current_user.id
        )
        
        db.session.add(post)
        db.session.commit()
        
        flash('Post created successfully!', 'success')
    else:
        flash('There was an error creating the post. Please check the form.', 'danger')
    
    return redirect(url_for('marketing.scheduler'))

@marketing_bp.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm(obj=post)
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.scheduled_date = form.scheduled_date.data
        post.platform = form.platform.data
        post.status = form.status.data
        
        db.session.commit()
        
        flash('Post updated successfully!', 'success')
        return redirect(url_for('marketing.scheduler'))
    
    return render_template('marketing/edit_post.html', form=form, post=post, title='Edit Post')

@marketing_bp.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('marketing.scheduler'))

@marketing_bp.route('/campaigns')
@login_required
def campaigns():
    campaigns = Campaign.query.order_by(Campaign.start_date.desc()).all()
    return render_template('marketing/campaigns.html', campaigns=campaigns, title='Marketing Campaigns')

@marketing_bp.route('/campaigns/create', methods=['GET', 'POST'])
@login_required
def create_campaign():
    form = CampaignForm()
    
    if form.validate_on_submit():
        metrics_file = None
        if form.metrics_file.data:
            metrics_file = save_file(form.metrics_file.data, directory='campaigns')
        
        campaign = Campaign(
            name=form.name.data,
            type=form.type.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            metrics_file=metrics_file,
            created_by=current_user.id
        )
        
        db.session.add(campaign)
        db.session.commit()
        
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('marketing.campaigns'))
    
    return render_template('marketing/create_campaign.html', form=form, title='Create Campaign')

@marketing_bp.route('/campaigns/<int:campaign_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    form = CampaignForm(obj=campaign)
    
    if form.validate_on_submit():
        campaign.name = form.name.data
        campaign.type = form.type.data
        campaign.description = form.description.data
        campaign.start_date = form.start_date.data
        campaign.end_date = form.end_date.data
        
        if form.metrics_file.data:
            campaign.metrics_file = save_file(form.metrics_file.data, directory='campaigns')
        
        db.session.commit()
        
        flash('Campaign updated successfully!', 'success')
        return redirect(url_for('marketing.campaigns'))
    
    return render_template('marketing/edit_campaign.html', form=form, campaign=campaign, title='Edit Campaign')

@marketing_bp.route('/campaigns/<int:campaign_id>/delete', methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    db.session.delete(campaign)
    db.session.commit()
    
    flash('Campaign deleted successfully!', 'success')
    return redirect(url_for('marketing.campaigns'))
