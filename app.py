from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contexte')
def context():
    title = "Contexte"
    content = r"""En entrant dans l'enceinte de l'IUT vous réveillez le <b>Tinausaure</b> qui vous pourchasse.<br>
    Il vous faudra rassembler la <b>Triforce CCNA</b>,<br>au cours de différentes étapes  pour vous <b>réconcilier</b> avec lui.
    """
    rappel="Entrez dans l'invite de commande GO pour commencer votre mission."
    return render_template('page.html', dino=True, fragments=None, title=title, content=content, rappel=rappel)

# routes for the three fragments
@app.route('/etape1')
def first_fragment():
    title = "Émettre la bonne fréquence"
    content = r"""Pour <b>brouiller les sens du Tinausaure</b> et gagner du temps, 
    vous devez <b>émettre une fréquence spécifique</b> à l'aide de votre appareil.
    <br>Bonne chance !<br><br>
    Retrouvez la fréquence <b>f</b> à émettre :<br><br>
    \(6 = \dfrac{\mathrm{Am}}{\mathrm{f}}\)"""
    rappel="Entrez dans l'invite de commande le code à 4 chiffres obtenu pour passer à la suite."

    return render_template('page.html', fragments=0, title=title, content=content, rappel=rappel)

@app.route('/etape2')
def second_fragment():
    # si nfc fonctionne pas, afficher un indice pour se connecter au wifi et afficher le portail captif

    title = "Se connecter au réseau"
    content = r"""<b>Un point d'accès Wi-Fi</b> est disponible à proximité.<br>
    Pour y accéder, veuillez vous connecter au réseau Wi-Fi et suivre les instructions.
    <br><br><b>Mot de passe:</b> le-tinausaure-arrive
    <br><br>Une fois connecté, faites maintenant appel au <b>portail captif</b> pour obtenir les données nécessaires à la suite de votre mission.
    <br><i><b>Indice:</b> Aller sur n'importe quel site web en http non sécurisé (ex: http://site.com/)</i>
    """
    rappel="Entrez dans l'invite de commande le code à 4 chiffres obtenu pour passer à la suite."

    return render_template('page.html', fragments=1, title=title, content=content, rappel=rappel)

@app.route('/etape3')
def third_fragment():
    title = "Localiser le fragment final"
    content = r"""Le <b>dernier fragment</b> de la triforce est <b>perdu</b> dans la nature.
    <br>Pour le récupérer, vous devez le <b>géocaliser</b> et le <b>scanner</b> sur un détecteur à triforce CCNA.
    """
    rappel="Entrez dans l'invite de commande le code à 4 chiffres obtenu pour passer à la suite."

    return render_template('page.html', fragments=2, title=title, content=content, rappel=rappel)

@app.route('/ending')
def ending():
    return render_template('end.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    # debug=True for development only
    app.run(debug=True, host='0.0.0.0', port=5000)
