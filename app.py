from flask import Flask, render_template
import stopwatch

app = Flask(__name__)


def add_malus(elapsed_seconds: float, malus_minutes: int) -> float:
    """Add malus time in minutes to elapsed seconds."""
    return elapsed_seconds + malus_minutes * 60



@app.route('/')
def index():
    return render_template('index.html', show_timer=False, timer_start=None)

@app.route('/contexte')
def context():
    title = "Contexte"
    content = r"""En entrant dans l'enceinte de l'IUT vous réveillez le <b>Tinausaure</b> qui vous pourchasse.<br>
    Il vous faudra rassembler la <b>Triforce CCNA</b>,<br>au cours de différentes étapes  pour vous <b>réconcilier</b> avec lui.
    """
    rappel="Entrez dans l'invite de commande GO pour commencer votre mission."
    stopwatch.start('global')
    start_epoch = stopwatch.get_start_wall_time('global')
    malus = stopwatch.get_malus_minutes('global')
    return render_template('page.html', dino=True, fragments=None, title=title, content=content, rappel=rappel, show_timer=True, timer_start=start_epoch)

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

    start_epoch = stopwatch.get_start_wall_time('global')
    malus = stopwatch.get_malus_minutes('global')
    return render_template('page.html', fragments=0, title=title, content=content, rappel=rappel, show_timer=True, timer_start=start_epoch)

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

    start_epoch = stopwatch.get_start_wall_time('global')
    malus = stopwatch.get_malus_minutes('global')
    return render_template('page.html', fragments=1, title=title, content=content, rappel=rappel, show_timer=True, timer_start=start_epoch)

@app.route('/etape3')
def third_fragment():
    title = "Localiser le fragment final"
    content = r"""Le <b>dernier fragment</b> de la triforce est <b>perdu</b> dans la nature.
    <br>Pour le récupérer, vous devez le <b>géocaliser</b> et le <b>scanner</b> sur un détecteur à triforce CCNA.
    """
    rappel="Entrez dans l'invite de commande le code à 4 chiffres obtenu pour passer à la suite."

    # apply automatic malus of 1 minute when reaching etape3
    stopwatch.add_malus_minutes('global', 1)

    start_epoch = stopwatch.get_start_wall_time('global')
    malus = stopwatch.get_malus_minutes('global')
    return render_template('page.html', fragments=2, title=title, content=content, rappel=rappel, show_timer=True, timer_start=start_epoch, malus=malus)

@app.route('/ending')
def ending():
    # apply an additional automatic malus of 1 minute on the ending page
    stopwatch.add_malus_minutes('global', 1)
    # stop the stopwatch when visiting ending (stop includes malus)
    elapsed = stopwatch.stop('global')
    malus = stopwatch.get_malus_minutes('global')
    # we can pass final elapsed to the template (optional)
    return render_template('end.html', show_timer=True, timer_start=None, final_elapsed=elapsed, malus=malus)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    # debug=True for development only
    app.run(debug=True, host='0.0.0.0', port=5000)
