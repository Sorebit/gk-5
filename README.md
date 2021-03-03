# Grafika 3D

## Installation

- Python 3.8
- `pip install -r requirements.txt`

## Usage

- `python main.py`

## Specyfikacja:

- [x] Jeden obiekt poruszający się (przesuwanie + obroty)
- [x] Kilka stałych obiektów. Jeden z nich gładki (np. interpolowana trójkatami sfera)
- [x] min 3 kamery (przełączanie):
    - [x] nieruchoma obserwująca scenę
    - [x] nieruchoma śledząca ruchomy obiekt
    - [x] związana z ruchomym obiektem
- [x] mozliwość zmiany trybu cieniowania (wypełniania trójkątów):
    - [ ] cieniowanie Gourauda
    - [x] cieniowanie Phonga
- [x] Kilka źródeł światła (min 3):
    - [x] min. jeden reflektor na poruszającym się obiekcie (np. światła samochodu)
    - [x] Musi istnieć możliwość zmiany kierunku świecenia reflektora (względnej) umieszczonego na obiekcie ruchomym
    - [x] Min. jedne stałe (nieporuszające się) żródło światła (punktowe lub reflektor)
- [x] mgła - płynna zmiana
- [x] noc/dzień - płynne zmiany
- [x] "zanikanie" światła wraz z odległością

### Dodatkowo jeden element do wyboru:

- [ ] lustro na scenie 
- [ ] odroczone cieniowanie (Deferred shading)

### Dokumentacja:

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
- `<- / ->` - Zmiana kierunku reflektora