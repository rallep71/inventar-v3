# app/models/team.py
"""Team model for multi-team support"""
from datetime import datetime
from app.extensions import db

# Association table for team members
team_members = db.Table('team_members',
    db.Column('team_id', db.Integer, db.ForeignKey('teams.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role', db.String(50), default='member'),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)


class Team(db.Model):
    """Team model"""
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Settings
    is_active = db.Column(db.Boolean, default=True)
    allow_guest_view = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    members = db.relationship('User', secondary=team_members, 
                            backref=db.backref('teams', lazy='dynamic'))
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<Team {self.name}>'
    
    def add_member(self, user, role='member'):
        """Add a member to the team"""
        if user not in self.members:
            self.members.append(user)
            # Update role in association table
            stmt = team_members.update().where(
                team_members.c.team_id == self.id,
                team_members.c.user_id == user.id
            ).values(role=role)
            db.session.execute(stmt)
    
    def remove_member(self, user):
        """Remove a member from the team"""
        if user in self.members:
            self.members.remove(user)
    
    def get_member_role(self, user):
        """Get role of a member"""
        result = db.session.query(team_members).filter_by(
            team_id=self.id,
            user_id=user.id
        ).first()
        return result.role if result else None
