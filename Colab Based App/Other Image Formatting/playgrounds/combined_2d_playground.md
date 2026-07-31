# pre-defined variables/values:
===============================
```python
y_title = 'Intensity'
x_title = 'Wavelength (nm)'
fig_size = (15,6)
prominence = 0.12
min_bright = 0.1
min_alpha = 0.1
min_alpha_scatter = 0.2
base_marker_size = 5
max_marker_size_factor = 95
gamma_factor = 0.8
bar_width = 1
smoothing_window = 5    # Increase this value to control the degree of smoothing
base_sigma_nm = 0.5 # Base width of the Gaussian (for low intensity peaks)
max_sigma_multiplier = 4.0 # How much wider the highest intensity peaks can be
x_min = 400
x_max = 750
reverse_x = True
show_grid = True
plot_type = None

x = df_filtered['nm'].values
y = df_filtered['Grey Val'].values

```

====================
# functions
====================
```python
def get_mode()       # determines dark vs. light mode
```
depends on:
- user input


```python
def text_colour()       # determines text colour based on mode
```
depends on:
- mode


```python
def dynamic_prominence(prominence, int_range)       # calculates dynamic prominence
```
depends on:
- prominence
- int_range


```python
def final_scale(min, factor)       # calculates final_alpha and final_intensity_scale
```
depends on:
- min_bright / min_alpha / min_alpha_scatter
- alpha_factor / int_factor


```python
def colored_rgb(base_rgb, final_intensity_scale)       # calcualtes the rgb conversion
```
depends on:
- base_rgb
- final_intensity_scale


```python
def axis_labels()       # sets the "theme" of the graph. universal for 2d plots
```
depends on:
- get_mode
- text_colour
- show_grid
- x_max
- x_min
- x_title
- y_title
- reverse_x
- fig_size


```python
def line_plot_iteration()       # generates the rgb line graph 
```
depends on:
- min_bright
  - final_scale
- colored_rgb


```python
def filled_plot_iteration()     # generates the filled in rgb line graph
```
depends on:
- rgb
- min_alpha
  - final_scale


```python
def peak_labels()       # currently only used by the first line plot
```
depends on:
- dyn_prom
  - prominence


```python
def gaussian_iteration()        # generates the gaussian rgb plot
```
depends on:
- rgb
- prominence
  - dyn_prominence
    - int_range
- min_alpha
- gamma_faactor
- base_sigma_nm
- max_sigma_multiplier


```python
def scatter_iteration()     # generates the scatter rgb plot
```
depends on:
- rgb
- base_marker_size
- max_marker_size_factor
- min_alpha_scatter
  - final_scale
- smoothing_window


```python
def bar_iteration()     # generates the rgb bar graph
```
depends on:
- rgb
- min_bright
- bar_width
- colored_rgb
- mode

