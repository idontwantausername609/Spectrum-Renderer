=============================================

## Line graph with red peak labels
=============================================


df_filtered = df[(df['nm'] >= 400) & (df['nm'] <= 750)].copy()
df_filtered = df_filtered.sort_values(by='nm').reset_index(drop=True)

plt.figure(figsize=(12, 7))
sns.lineplot(data=df_filtered, x='nm', y='Grey Val', marker=None)
plt.title('Grey Val vs. nm (nm range 400-750) with Sharp Peak Labels', color='white')
plt.xlabel('nm')
plt.ylabel('Grey Val')
plt.grid(True, color='darkgrey', linestyle=':')

plt.xticks(color='white') 
plt.yticks(color='white')
plt.xlabel('Wavelength (nm)', color='white')
plt.ylabel('Grey Val (Intensity)', color='white') 

ax = plt.gca()
ax.set_facecolor('black')
plt.gcf().set_facecolor('black')

# Set x-axis limits and reverse the order
plt.xlim(750, 400)

# --- Dynamic Prominence Calculation ---
min_grey_val = df_filtered['Grey Val'].min()
max_grey_val = df_filtered['Grey Val'].max()
grey_val_range = max_grey_val - min_grey_val

prominence_percentage = 0.12 
dynamic_prominence = prominence_percentage * grey_val_range

# A higher prominence value will select fewer, stronger peaks.
peaks, _ = find_peaks(df_filtered['Grey Val'], prominence=dynamic_prominence)

# Label the identified sharp peaks
for peak_index in peaks:
    row = df_filtered.iloc[peak_index]
    plt.annotate(f"{row['nm']:.2f} nm", # Formatted nm to two decimal places
                 (row['nm'], row['Grey Val']),
                 textcoords="offset points", # Offset the text
                 xytext=(0,10), # Distance from point to label
                 ha='center', # Horizontal alignment
                 bbox=dict(boxstyle="round,pad=0.3", fc="red", ec="b", lw=0.5, alpha=0.7),
                 arrowprops=dict(facecolor='black', shrink=0.05))

plt.show()

=============================================
## RGB line graph - light mode
=============================================

# Normalize Grey Val for intensity scaling
min_grey_val = df_filtered['Grey Val'].min()
max_grey_val = df_filtered['Grey Val'].max()
grey_val_range = max_grey_val - min_grey_val

# Avoid division by zero if all Grey Vals are the same
if grey_val_range == 0:
    df_filtered['Normalized_Grey_Val'] = 1.0
else:
    df_filtered['Normalized_Grey_Val'] = (df_filtered['Grey Val'] - min_grey_val) / grey_val_range

plt.figure(figsize=(15, 6))

for i in range(len(df_filtered) - 1):
    wavelength_start = df_filtered.iloc[i]['nm']
    wavelength_end = df_filtered.iloc[i+1]['nm']

    # Use the normalized Grey Val of the first point in the segment for intensity
    grey_val_intensity_factor = df_filtered.iloc[i]['Normalized_Grey_Val']

    base_rgb = rgb(wavelength_start)
    min_brightness = 0.1 
    final_intensity_scale = min_brightness + (1 - min_brightness) * grey_val_intensity_factor

    colored_rgb = (base_rgb[0] * final_intensity_scale,
                   base_rgb[1] * final_intensity_scale,
                   base_rgb[2] * final_intensity_scale)

    plt.plot([wavelength_start, wavelength_end],
             [df_filtered.iloc[i]['Grey Val'], df_filtered.iloc[i+1]['Grey Val']],
             color=colored_rgb,
             linewidth=2)

plt.title('Emission Spectrum with RGB Color Representation')
plt.xlabel('Wavelength (nm)')
plt.ylabel('Grey Val (Intensity)')
plt.xlim(750, 400) 
plt.grid(True)
plt.show()

print("This plot displays the emission spectrum where each segment's color is determined by its wavelength, and its brightness is modulated by its 'Grey Val' (intensity).")
print("The 'rgb' function maps wavelengths to corresponding colors in the visible spectrum, and the 'Normalized_Grey_Val' adjusts the perceived brightness of these colors.")

=============================================
## RGB flilled line graph
=============================================

min_grey_val = df_filtered['Grey Val'].min()
max_grey_val = df_filtered['Grey Val'].max()
grey_val_range = max_grey_val - min_grey_val

if grey_val_range == 0:
    df_filtered['Normalized_Grey_Val'] = 1.0
else:
    df_filtered['Normalized_Grey_Val'] = (df_filtered['Grey Val'] - min_grey_val) / grey_val_range

plt.figure(figsize=(15, 6))
ax = plt.gca() # Get current axes

for i in range(len(df_filtered) - 1):
    wavelength_start = df_filtered.iloc[i]['nm']
    wavelength_end = df_filtered.iloc[i+1]['nm']

    # Use the wavelength at the start of the segment for color mapping
    base_rgb = rgb(wavelength_start)

    alpha_factor = df_filtered.iloc[i]['Normalized_Grey_Val']
    min_alpha = 0.1 
    final_alpha = min_alpha + (1 - min_alpha) * alpha_factor

    plt.fill_between([wavelength_start, wavelength_end],
                     [0, 0], # Base of the fill is y=0
                     [df_filtered.iloc[i]['Grey Val'], df_filtered.iloc[i+1]['Grey Val']], 
                     color=base_rgb,
                     alpha=final_alpha,
                     linewidth=0) # No line for the fill edges

    plt.plot([wavelength_start, wavelength_end],
             [df_filtered.iloc[i]['Grey Val'], df_filtered.iloc[i+1]['Grey Val']],
             color=base_rgb,
             linewidth=2) # Thicker line for better visibility on top of fill


plt.title('Emission Spectrum with RGB Filled Representation')
plt.xlabel('Wavelength (nm)')
plt.ylabel('Grey Val (Intensity)')
plt.xlim(750, 400)
plt.grid(True)
plt.show()

print("This plot now displays the emission spectrum with the area under the curve filled with wavelength-dependent colors.")
print("The intensity of the emitted light (Grey Val) now directly influences the opacity (alpha) of the filled region, creating a more vivid 'glowing' effect for brighter emissions, similar to how emission spectra are often presented.")