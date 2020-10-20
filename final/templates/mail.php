{% extends "layout.html"}

{% block title %}Something Went Wrong!{% endblock %}

{% block content %}
    <?php
        $to      = 'joshiy390@gmail.com';
        $subject = 'the subject';
        $message = 'hello';

        mail($to, $subject, $message);
    ?>

    <form name="regmail" id="regmail" action="/login" method="POST">
        <input name="test" value="test">
        <input type="submit" value="Submit">
    </form>
{% endblock %}