# pre-defined variables/values:
===============================
```python
min_int = df_filtered['Grey Val'].min()
max_int = df_filtered['Grey Val'].max()
int_range = max_int - min_int
rgb = utils.wavelength_to_rgb
y_title = 'Intensity'
x_title = 'Wavelength (nm)'
fig_size = (15,6)
prominence = 0.12
dyn_prom = prominence * int_range
min_bright = 0.1
min_alpha = 0.1
x_min = 400
x_max = 750
mode = 'dark'
reverse_x = True
show_grid = True

```

====================
# functions
====================
```python
def axis_labels()       # sets the "theme" of the graph. universal for 2d plots
```
depends on:
- mode
- show_grid
- x_max
- x_min
- x_title
- y_title
- reverse_x


```python
def line_plot_iteration()       # generates the rgb line graph 
```
depends on:
- fig_size
- min_bright
- rgb


```python
def filled_plot_iteration()     # generates the filled in rgb line graph
```
depends on:
- fig_size
- rgb
- min_alpha


```python
def peak_labels()       # currently only used by the first line plot
```
depends on:
- dyn_prom
  - prominence
