# Grafika 3D

## Installation

- Python 3.8
- `pip install -r requirements.txt`

## Usage

- `python main.py`

## Specyfikacja:

- [ ] Jeden obiekt poruszający się (przesuwanie + obroty)
- [ ] Kilka stałych obiektów. Jeden z nich gładki (np. interpolowana trójkatami sfera)
- [x] min 3 kamery (przełączanie):
    - [x] nieruchoma obserwująca scenę
    - [x] nieruchoma śledząca ruchomy obiekt
    - [ ] związana z ruchomym obiektem
- [x] mozliwość zmiany trybu cieniowania (wypełniania trójkątów):
    - [ ] cieniowanie Gourauda
    - [x] cieniowanie Phonga
- [ ] Kilka źródeł światła (min 3):
    - [ ] min. jeden reflektor na poruszającym się obiekcie (np. światła samochodu)
    - [ ] Musi istnieć możliwość zmiany kierunku świecenia reflektora (względnej) umieszczonego na obiekcie ruchomym
    - [ ] Min. jedne stałe (nieporuszające się) żródło światła (punktowe lub reflektor)
- [x] mgła - płynna zmiana
- [ ] noc/dzień - płynne zmiany
- [x] "zanikanie" światła wraz z odległością

Dodatkowo jeden element do wyboru:
- [ ] lustro na scenie 
- [ ] odroczone cieniowanie (Deferred shading)


    Przykładowe projekty dla CPU/GPU
    
    - szachy
    - bilard
    - kręgle
    - samochód z reflektorami w mieście - noc/dzień
    - "straż pożarna"
    - "iluminacje" świąteczne
    - robot z "drzewem" połączeń
    - pociąg po "starych" szynach
    - kolejka linowa + wiatr
    - wyścigi samochodowe

- [ ] uaktualniona dokumentacja (przyjęte rozwiązania techniczne oraz 'user manual')
- [ ] krótki 30-60 sek. film z działania aplikacji.

## Klawiszologia

### Kamera

- `1` - Kamera statyczna
- `2` - Kamera podążająca za obiektem
- `3` - Kamera "przyczepiona" do obiektu
  
### Cieniowanie

- `O` - Gouraud
- `P` - Phong
- `F` - Mgła