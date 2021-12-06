from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///many_to_many.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['DEBUG'] = True

db = SQLAlchemy(app)

subs = db.Table('subs',

                db.Column('post_id', db.ForeignKey('post.id')),
                db.Column('tag_id', db.ForeignKey('tag.id'))
                )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    posts = db.relationship('Post', backref=db.backref('author', lazy=True))

    def __repr__(self):
        return f'User({self.id}, {self.name})'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tags = db.relationship('Tag', secondary=subs, backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return f'Post({self.id}, {self.title})'


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    def __repr__(self):
        return f'Tag({self.id}, {self.name})'


def create_data():
    user = User(name='Михаил')
    post = Post(title='Новый пост')
    user.posts.append(post)
    tag = Tag(name='flask')
    post.tags.append(tag)
    db.session.add_all([user, post, tag])
    db.session.commit()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Tag': Tag, 'subs': subs, 'create_data': create_data}


@app.route('/')
def index():
    all_tags = Tag.query.all()
    return render_template('index.html', all_tags=all_tags)


@app.route('/tag/<string:post_str>')
def post_tags(post_str):
    single_tag = Tag.query.filter_by(name=post_str).first()
    print(single_tag)
    return render_template('post_tags.html', single_tag=single_tag)


@app.route('/post/<string:tag_str>')
def tag_posts(tag_str):
    single_post = Post.query.filter_by(title=tag_str).first()
    return render_template('tag_posts.html', single_post=single_post)


if __name__ == '__main__':
    db.create_all()
    create_data()
    app.run()
