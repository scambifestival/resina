# _Resina_ Bot - Introduzione

Questa repository contiene il codice sorgente di [`r3sinabot`](https://t.me/r3sinabot 'Resina bot on Telegram').

Per sapere ciò su cui stiamo lavorando, vedi [_Scambi Telegram Bot_ project](https://github.com/orgs/scambifestival/projects/4).

<ins>Nota</ins>: _Resina_ Bot è ancora in fase di sviluppo.

# Cos'è _Resina_

_Resina_ è un bot pensato per ausiliare lo staff di [Scambi](https://scambi.org) nell'organizzazione interna nonché favorirne la comunicazione e facilitarne l'uso di alcuni strumenti istitutivi attraverso alcune funzionalità, tra le quali:

1. automatizzazione dell'iscrizione dei nuovi membri alla nostra associazione, tramite:
>- creazione degli account sulle nostre piattaforme;
>- giunta dell'utente al nostro libro soci;
2. facilitazione dell'uso di Pino, il nostro database, da dispositivi mobili;
3. collezione delle idee proposte, catalogate tramite appositi hashtag;

ed altre funzioni ancora in fase di progettazione.

## Struttura dello script

Lo script del bot, interamente programmato in Pyhton attraverso la libreria [Python Telegram Bot](https://github.com/python-telegram-bot/python-telegram-bot), è articolato in diversi moduli:
- `main.py` costituisce il core dello script. Al suo interno è definito lo scheletro del bot e descritto il suo comportamento generale;
- `dispatcher.py` costituisce l'espressione pratica del comportamento di Resina; in base al valore di ritorno, passato tramite il `main`, lancia la funzione adibita allo scopo;
- `db_functions.py` contiene tutte le funzioni utili all'interazione col database interno, tra cui la connessione e la formulazione di _queries_;
- `utils.py` è una sorta di coltellino svizzero che offre funzioni che possono risultare utili agli altri moduli, come la formulazione della risposta testuale del bot o il salvataggio delle informazioni relative ad un utente;
- `variables.py` include tutte quelle variabili che sono necessarie agli altri moduli al fine di garantire il corretto funzionamento dell'intero script.

## Il database

_Resina_ interagisce con un database interno basato su [SQLite](https://www.sqlite.org/) attraverso la libreria `sqlite3`.

Esso consente di fornire protezione dallo spam e di facilitare l'uso del bot da parte di utenti che ne hanno già fatto uso.

_Nota_: non si esclude che possa avere altri scopi in futuro.

