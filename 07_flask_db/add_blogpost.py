from app import db, BlogPost

#blog_post1 = BlogPost("Blog Title1", "Blog Test1", "Image1.png", 1, "Summary1")
#blog_post2 = BlogPost("Blog Title2", "Blog Test2", "Image2.png", 1, "Summary2")
#blog_post3 = BlogPost("Blog Title3", "Blog Test3", "Image3.png", 3, "Summary3")

blog_post4 = BlogPost("Blog Title4", "Blog Test4", "Image4.png", 4, "Summary4")

#db.session.add_all([blog_post1, blog_post2, blog_post3])
db.session.add(blog_post4)
db.session.commit()