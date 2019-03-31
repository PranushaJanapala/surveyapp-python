

def sendmail(mail_list,department):
    #mail=Mail(app)
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'pranushajanapala@gmail.com'
    app.config['MAIL_PASSWORD'] = 'sreerama1234'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_DEFAULT_SENDER'] = 'pranushajanapala@gmail.com'
    mail=Mail(app)

    msg = Message('Hello',  recipients=['pranushajanapala@gmail.com'])
    msg.body = "please take the survey"
    mail.send(msg)
    return " Mail send to user under '+ department +' department"