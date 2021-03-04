# Grafika 3D

## Installation

- Python 3.8
- `pip install -r requirements.txt`

## Usage

- `python main.py`

## Przyjęte rozwiązania techniczne:

- `glfw` - Tworzenie okna
- `pyopengl` - Bindy do renderowania w OpenGL
- `pyrr` + `numpy` - Operacja na wektorach i macierzach
- `pillow` - Wczytywanie obrazów
- `pywavefront` - Wczytywanie plików `*.obj` i `*.mtl`

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