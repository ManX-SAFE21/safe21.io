# Guida al sito SAFE21

Come è fatto questo sito e come si aggiunge un articolo al blog, senza rompere
niente.

Il registro di *cosa* è stato fatto, task per task, sta in [CHANGELOG.md](CHANGELOG.md).
Questo file spiega invece *come* si fa.

---

## 1. Com'è fatto il sito

Pagine **HTML statiche**: nessun framework, nessun build step, nessun bundler,
nessuna dipendenza da installare.

Dal CHANGELOG #42 le pagine del blog **non sono più autoconsistenti**: caricano
due file condivisi, **`blog.css`** (tutto lo stile) e **`blog.js`** (menu mobile,
tema chiaro/scuro, lightbox). Prima ogni pagina ne portava la propria copia:
erano ~525 righe identiche ripetute dieci volte.

Conseguenza pratica, opposta a quella di prima: **se modifichi `blog.css`
cambiano tutte le pagine del blog insieme.** Comodo per una modifica voluta,
pericoloso per una distratta — controlla sempre più di una pagina.

Restano invece copiati in ogni pagina, di proposito: **header e footer**
(estrarli richiederebbe un build step o l'iniezione via JavaScript, che
penalizza SEO e lettori senza JS) e il **piccolo script anti-flash** nel
`<head>`, che deve girare prima del primo rendering.

`index.html` (la homepage) è a parte e resta interamente autoconsistente.

```
index.html                     homepage (inglese, con switcher EN/IT a runtime)
blog.html                      indice degli articoli
blog-<slug>.html               un file per articolo
images/                        immagini degli articoli
logos/                         logo e favicon
sitemap.xml  robots.txt        SEO
safe21-pgp.asc                 chiave pubblica OpenPGP
.well-known/security.txt       contatto di sicurezza (standard RFC 9116)
.claude/launch.json            config del server di anteprima locale
```

### Regole fisse, decise dal committente

- **Il blog è solo in italiano.** Nessuno switcher di lingua, nessun dizionario
  i18n: il testo italiano è scritto direttamente nel markup. Solo `index.html`
  ha lo switcher EN/IT.
- **Codice e commenti in inglese.** Vale per i commenti HTML/CSS/JS dentro le
  pagine. Il testo visibile all'utente resta italiano.
- **Tema chiaro/scuro** su ogni pagina del blog. Il default è scuro; la scelta
  vive in `sessionStorage` sotto la chiave `safe21-blog-theme`, quindi dura
  solo per la visita in corso. La homepage usa una chiave diversa
  (`safe21-lang`, per la lingua): non vanno confuse.

---

## 2. Aggiungere un articolo: le 4 modifiche

Un articolo nuovo richiede **quattro modifiche coordinate**. Se ne salti una il
sito non dà errori — semplicemente l'articolo non compare, o non viene indicizzato.

### Passo 1 — Crea la pagina

Duplica una pagina **recente** (per esempio `blog-caso-liquid.html`): collega
già `blog.css` e `blog.js` invece di incorporarli. Tutti i blocchi di stile sono
disponibili su ogni pagina, quindi la scelta del modello non è più vincolante
come prima — conta solo che abbia la struttura che ti serve (con o senza
immagine).

Poi aggiorna, nel `<head>`:

| Campo | Nota |
|---|---|
| `<title>` | Titolo — SAFE21. **Max ~70 caratteri**, altrimenti Google lo tronca |
| `<meta name="description">` | **Max ~160 caratteri** |
| `og:title` / `og:description` | Di solito uguali ai due sopra |
| `og:url` | `https://safe21.io/<slug>` — **senza** `.html` |
| `og:image` | URL assoluto dell'immagine, solo se l'articolo ne ha una |
| `<link rel="canonical">` | `https://safe21.io/<slug>.html` — **con** `.html` |
| JSON-LD | `headline` deve corrispondere **esattamente** all'`<h1>`; `url` deve corrispondere al canonical; `datePublished` / `dateModified` |

> `og:url` senza estensione e `canonical` con `.html` è voluto, non un errore:
> rispecchia come Cloudflare serve le pagine (vedi § 6).

Nel corpo aggiorna `.eyebrow` (la categoria), `<h1>`, `.standfirst` e `.byline`
(autore, data in italiano, minuti di lettura).

**Minuti di lettura:** conta le parole del testo e dividi per 200. Il numero
nella byline deve corrispondere a quello della card in `blog.html`.

### Passo 2 — Card in `blog.html`

Aggiungi un blocco `<a class="post-card">` **in cima** alla lista (gli articoli
sono in ordine dal più recente). Data, categoria e minuti di lettura devono
essere **identici** a quelli della pagina dell'articolo.

### Passo 3 — JSON-LD in `blog.html`

Nello stesso file, aggiungi una voce `BlogPosting` in cima all'array
`blogPost[]`. **L'ordine deve essere lo stesso delle card.**

### Passo 4 — `sitemap.xml`

Aggiungi un blocco `<url>` con `<loc>`, `<lastmod>`, `<changefreq>monthly`,
`<priority>0.7`. Aggiorna anche il `<lastmod>` di `blog.html`, che è cambiato.

### Passo 5 — `CHANGELOG.md`

Aggiungi una voce numerata in cima (`## [N] — ...`), con data e stato. Quando
hai pushato, imposta lo stato a `Delivered and live (commit <hash>, pushed to main)`.

---

## 3. I blocchi di stile disponibili

Fino al CHANGELOG #41 ogni pagina aveva il proprio `<style>` e i blocchi erano
stati sfoltiti pagina per pagina: bisognava controllare in una tabella se il
modello che copiavi conteneva quello che ti serviva.

**Da #42 non serve più:** lo stile sta tutto in `blog.css`, che ogni pagina
carica per intero. Tutti i blocchi qui sotto sono quindi sempre disponibili.
Per verificarlo:

```bash
python tools/audit.py --css-matrix
```

Se aggiungi uno stile nuovo, va in `blog.css` — **mai** in un `<style>` dentro
la pagina, altrimenti riparte la divergenza che abbiamo appena eliminato.

A cosa servono:

- **`.callout`** — riquadro colorato per un'idea chiave. *Massimo uno per
  articolo*, altrimenti perde forza.
- **`figure.source`** — contenitore dell'immagine, con didascalia opzionale.
- **lightbox** — click sull'immagine per ingrandirla a dimensione reale 1:1.
  Serve solo se la pagina ha immagini: richiede sia il CSS sia il `<div
  class="lightbox-overlay">` a inizio `<body>` sia il blocco JS in fondo.
- **`.table-wrap`** — tabella dati. Scorre dentro il proprio riquadro, così la
  pagina non scorre mai di lato sul telefono.
- **`a.inline`** — link dentro il testo (sottolineati).
- **`.footnote`** — blocco finale con fonti e disclaimer.
- **`code`** — chip monospace per stringhe brevi.

### Il footer deve restare identico su tutte le pagine

La colonna **Contatti** contiene sempre, nello stesso ordine:

```
info@safe21.io  ·  Blog  ·  Codice open source ↗  ·  Chiave PGP
```

`index.html` è l'unica eccezione strutturale: usa chiavi i18n
(`footer.github`, `footer.pgp`) e applica le traduzioni via `innerHTML`, quindi
le entità HTML come `&nearr;` vanno messe **dentro** il valore del dizionario.

---

## 4. Immagini

Convertile sempre in **WebP** e mettile in `images/`. Obiettivo: circa **60 KB**.

**Quale compressione usare dipende dal tipo di immagine** — non c'è una regola
unica:

| Tipo | Metodo | Perché |
|---|---|---|
| Grafici, diagrammi, schemi a tinte piatte | **lossless** | Comprime meglio del lossy su aree uniformi e il testo resta perfettamente nitido quando si ingrandisce |
| Foto, illustrazioni con sfumature | **lossy, qualità 90-95** | Il lossless su una foto produce file enormi |

Esempio reale (articolo #31): il grafico in lossless pesa 60 KB, mentre in
lossy qualità 95 faceva 144 KB. Sulla copertina illustrata è vero il contrario.

```python
from PIL import Image
im = Image.open('originale.png').convert('RGB')
im.save('images/nome.webp', 'WEBP', lossless=True, method=6)   # grafici
im.save('images/nome.webp', 'WEBP', quality=95,   method=6)    # foto
```

### ⚠️ `width` e `height` devono essere i pixel reali del file

```html
<img src="images/nome.webp" width="2086" height="980" ... />
```

Se i numeri non corrispondono al file, il browser riserva lo spazio sbagliato e
la pagina **salta** quando l'immagine finisce di caricare. È già successo una
volta (bug corretto nell'audit #30: dichiarava 804 px invece di 725).

Verifica sempre:

```python
from PIL import Image; print(Image.open('images/nome.webp').size)
```

L'`alt` è obbligatorio e deve **descrivere** l'immagine, non solo nominarla:
è quello che leggono screen reader e motori di ricerca.

---

## 5. Trappole note

**Le media query vanno DOPO le regole base.** In `blog.css` molte regole hanno
la stessa specificità: a parità di specificità vince l'ultima scritta. Una `@media` messa sopra la regola base è CSS morto e
non dà nessun errore.

```css
.article-body td { padding: 13px 16px; }        /* base */

@media (max-width: 760px) {                      /* override: DEVE stare dopo */
  .article-body td { padding: 11px 13px; }
}
```

**Il tema scuro nasconde gli errori sulle ombre.** In modalità scura
`--card-shadow` vale `none`, quindi un'ombra sbagliata è invisibile. **Controlla
sempre anche il tema chiaro** prima di pubblicare.

**Attenzione alle due righe in fondo a `blog.css`.** Sono le regole che elencano
quali elementi hanno la transizione di tema e quali l'ombra:

```css
body, header, .callout, figure.source, .table-wrap { transition: ... }
.callout, figure.source, .table-wrap { box-shadow: var(--card-shadow); }
```

**Regola:** ogni pannello — `.callout`, `figure.source`, `.table-wrap` e le
classi specifiche come `.checklist` o `.rule` — va in *entrambi* gli elenchi.
Uniformato in #33 e ora dichiarato una volta sola in `blog.css` (#42).

Aggiungere o togliere un selettore qui cambia la resa in tema chiaro **senza
che si veda nulla in tema scuro**, perché lì `--card-shadow` vale `none`. Se ci
metti mano, confronta prima e dopo in tema chiaro.

**La homepage fa scattare falsi allarmi.** `index.html` ha `<html lang="en">` e
canonical/`og:url` che puntano alla radice `https://safe21.io/`. **È corretto:**
la homepage è inglese e lo script i18n riscrive `lang` a runtime.

---

## 6. Anteprima e pubblicazione

### In locale

```bash
python -m http.server 8177
```

Poi apri `http://localhost:8177/blog.html`. (È anche la config in
`.claude/launch.json`.) Serve un server vero: aprire il file con `file://`
non riproduce il comportamento reale.

### Pubblicare

**Il deploy è automatico: un push su `main` va online in 1-3 minuti** tramite
Cloudflare Pages. Non c'è passaggio di staging — quello che pushi è pubblicato.

Due comportamenti di Cloudflare che sembrano bug ma non lo sono:

- **URL con `.html` rispondono `308`** e reindirizzano alla versione senza
  estensione. `https://safe21.io/blog-password-electrum.html` →
  `https://safe21.io/blog-password-electrum`. Con `curl` usa `-L`.
- **Le email vengono offuscate.** Ogni `mailto:` diventa
  `/cdn-cgi/l/email-protection#…` con uno script di decodifica. È protezione
  antispam automatica: l'HTML online non sarà mai identico a quello del repo.
- Subito dopo il push, un percorso non ancora compilato può restituire la
  homepage con codice 200 invece di un 404. Vuol dire solo che la build è
  ancora in corso.

---

## 7. Il controllo automatico

Prima di ogni push:

```bash
python tools/audit.py
```

Controlla in un colpo solo tutte le cose che è facile sbagliare e che **non
danno errore da sole**: annidamento HTML, JSON-LD valido e coerente con
l'`<h1>`, canonical e `og:url`, link e immagini che non esistono, `alt`
mancanti, `width`/`height` diversi dai pixel reali, footer allineato su tutte le
pagine, card ↔ JSON-LD ↔ sitemap ↔ file coerenti fra loro, data e minuti di
lettura uguali fra card e articolo, `id` duplicati, `target="_blank"` senza
`rel="noopener"`, numerazione del CHANGELOG, e che `safe21-pgp.asc` non
contenga per sbaglio una chiave privata.

Distingue due livelli:

- **ERRORE** — è rotto, va corretto prima di pushare. Lo script esce con codice
  `1`, quindi si può collegare a una CI.
- **AVVISO** — da valutare, non blocca (per esempio una meta description più
  lunga di 160 caratteri).

Output quando è tutto a posto:

```
✓ Nessun errore. Si può pushare. (9 avvisi da valutare.)
```

**Non segnala falsi allarmi.** Le eccezioni corrette e volute — come
`index.html` che ha `lang="en"` e il canonical sulla radice — sono elencate
nella costante `EXPECTED` in cima allo script, con il motivo. Se aggiungi una
nuova eccezione legittima, mettila lì invece di ignorare l'output: uno script
che segnala sempre gli stessi tre errori innocui smette di essere letto, e a
quel punto non serve più a niente.

Il controllo sulle dimensioni delle immagini richiede Pillow (`pip install
Pillow`); senza, il resto gira lo stesso e quel singolo controllo viene
dichiarato saltato.

---

## 8. Checklist prima del push

Prima di tutto:

```bash
python tools/audit.py
```

Lo script copre da solo i punti contrassegnati con 🤖. Restano da verificare a
mano quelli visivi:

- [ ] 🤖 `headline` del JSON-LD **identico** all'`<h1>`
- [ ] 🤖 `canonical` con `.html`, `og:url` senza
- [ ] 🤖 `<title>` ≤ 70 caratteri, `description` ≤ 160
- [ ] 🤖 Voce JSON-LD in `blog.html`, **nello stesso ordine** delle card
- [ ] 🤖 Data, categoria e minuti di lettura **uguali** tra card e articolo
- [ ] 🤖 Blocco in `sitemap.xml` presente
- [ ] 🤖 `width`/`height` delle immagini = pixel reali, `alt` presente
- [ ] 🤖 Footer identico alle altre pagine (4 link in Contatti)
- [ ] Card in `blog.html` aggiunta **in cima** (l'ordine cronologico non è verificabile in automatico)
- [ ] `lastmod` di `blog.html` aggiornato nella sitemap
- [ ] Immagini convertite in **WebP**, con l'`alt` che *descrive* davvero l'immagine
- [ ] Provato in tema **chiaro e scuro**
- [ ] Provato a **375 px** di larghezza (la pagina non deve scorrere di lato)
- [ ] Lightbox: apre e chiude (click sullo sfondo, X, Esc)
- [ ] Zero errori nella console del browser
- [ ] Voce nel `CHANGELOG.md`

Dopo il push, verifica che sia davvero online:

```bash
curl -sL -o /dev/null -w "%{url_effective} %{http_code}\n" https://safe21.io/<slug>.html
```
