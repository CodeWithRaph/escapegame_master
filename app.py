from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contexte')
def contact():
    return render_template('page.html')

# routes for the three fragments
@app.route('/etape1')
def first_fragment():
    title = "Émettre la bonne fréquence"
    content = r"""Pour brouiller les sens du dinosaure et gagner du temps, 
    vous devez émettre une fréquence spécifique à l'aide de votre appareil.
    <br>Bonne chance !<br><br>
    Retrouvez la fréquence f à émettre :<br><br>
    \(6 = \dfrac{\mathrm{am}}{\mathrm{fm}}\)"""

    return render_template('page.html', fragments=0, title=title, content=content)

@app.route('/etape2')
def second_fragment():
    # si nfc fonctionne pas, afficher un indice pour se connecter au wifi et afficher le portail captif
    return render_template('page.html', fragments=1)

@app.route('/etape3')
def third_fragment():
    # dire qu'il faut geolocaliser le dernier fragment
    return render_template('page.html', fragments=2)

@app.route('/ending')
def ending():
    return render_template('end.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    # debug=True for development only
    app.run(debug=True, host='0.0.0.0', port=5000)
