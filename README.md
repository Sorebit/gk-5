# Grafika 3D

## Podstawowa specyfikacja dla projektów na CPU:

- [ ] Jeden obiekt poruszający się (przesuwanie + obroty)
- [ ] Kilka stałych obiektów. Jeden z nich gładki (np. interpolowana trójkatami sfera)
- [ ] min 3 kamery (przełączanie):
    - [ ] nieruchoma obserwująca scenę
    - [ ] nieruchoma śledząca ruchomy obiekt
    - [ ] związana z ruchomym obiektem
- [ ] mozliwość zmiany trybu cieniowania (wypełniania trójkątów):
    - [ ] cieniowanie Gourauda
    - [ ] cieniowanie Phonga
- [ ] Kilka źródeł światła (min 3):
    - [ ] min. jeden reflektor na poruszającym się obiekcie (np. światła samochodu)
    - [ ] Musi istnieć możliwość zmiany kierunku świecenia reflektora (względnej) umieszczonego na obiekcie ruchomym
    - [ ] Min. jedne stałe (nieporuszające się) żródło światła (punktowe lub reflektor)
- [ ] mgła - płynna zmiana

OpenGL (dodatkowo):
- [ ] noc/dzień - płynne zmiany
- [ ] "zanikanie" światła wraz z odległością

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

Projekty nalezy oddawać osobiście. Proszę przygotować uaktualnioną dokumentację (przyjęte rozwiązania techniczne oraz 'user manual') oraz krótki 30-60 sek. film z działania aplikacji.