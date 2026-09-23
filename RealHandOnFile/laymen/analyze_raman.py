"""Analyze Raman spectra data files to find key peaks."""
import os

data_dir = r"e:\latex_AI\RealHandOnFile\laymen\ReportTemplate\data"
files = {
    "a(2).txt": "酒精 (Ethanol)",
    "b(1).txt": "白药片 (White tablet)",
    "si(1).txt": "硅 (Silicon)",
    "w(1).txt": "黑药片 (Black tablet / reference)"
}

def find_peaks(raman_shifts, intensities, min_distance=5, threshold_ratio=0.03):
    """Simple peak finding: find local maxima above threshold."""
    max_intensity = max(intensities)
    threshold = max_intensity * threshold_ratio
    
    peaks = []
    for i in range(1, len(intensities) - 1):
        if intensities[i] > threshold and intensities[i] > intensities[i-1] and intensities[i] > intensities[i+1]:
            # Check if it's a true local max (check further neighbors)
            is_peak = True
            for j in range(max(0, i-min_distance), min(len(intensities), i+min_distance+1)):
                if j != i and intensities[j] > intensities[i]:
                    is_peak = False
                    break
            if is_peak:
                peaks.append((raman_shifts[i], intensities[i]))
    
    # Sort by intensity descending
    peaks.sort(key=lambda x: x[1], reverse=True)
    return peaks

for fname, desc in files.items():
    fpath = os.path.join(data_dir, fname)
    if not os.path.exists(fpath):
        print(f"File not found: {fpath}")
        continue
    
    raman_shifts = []
    intensities = []
    
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        in_data = False
        for line in f:
            if 'Begin Spectral Data' in line:
                in_data = True
                continue
            if not in_data:
                # Read header info
                if '积分时间' in line or '积分时间' in line.encode('utf-8', errors='ignore').decode('gbk', errors='ignore'):
                    print(f"  {line.strip()}")
                continue
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    rs = float(parts[0])
                    intens = float(parts[1])
                    raman_shifts.append(rs)
                    intensities.append(intens)
                except ValueError:
                    continue
    
    if not raman_shifts:
        print(f"No data found in {fname}")
        continue
    
    print(f"\n{'='*60}")
    print(f"File: {fname} - {desc}")
    print(f"Data points: {len(raman_shifts)}")
    print(f"Raman shift range: {raman_shifts[0]:.1f} to {raman_shifts[-1]:.1f} cm⁻¹")
    print(f"Intensity range: {min(intensities):.1f} to {max(intensities):.1f}")
    
    # Find peaks
    peaks = find_peaks(raman_shifts, intensities, min_distance=8, threshold_ratio=0.02)
    print(f"\nTop 20 peaks (Raman shift, intensity):")
    for i, (rs, intens) in enumerate(peaks[:20]):
        print(f"  {i+1}. {rs:.1f} cm⁻¹: {intens:.1f}")
    
    # Also find specific known peak regions for common materials
    print(f"\nKey region scans:")
    # Silicon: ~520 cm⁻¹
    si_region = [(rs, intens) for rs, intens in zip(raman_shifts, intensities) if 500 <= rs <= 540]
    if si_region:
        max_si = max(si_region, key=lambda x: x[1])
        print(f"  Si 520 region: max at {max_si[0]:.1f} cm⁻¹ = {max_si[1]:.1f}")
    
    # C-H stretch region: 2800-3100 cm⁻¹
    ch_region = [(rs, intens) for rs, intens in zip(raman_shifts, intensities) if 2800 <= rs <= 3100]
    if ch_region:
        max_ch = max(ch_region, key=lambda x: x[1])
        print(f"  C-H stretch (2800-3100): max at {max_ch[0]:.1f} cm⁻¹ = {max_ch[1]:.1f}")
    
    # Fingerprint region: 400-1800
    fp_region = [(rs, intens) for rs, intens in zip(raman_shifts, intensities) if 400 <= rs <= 1800]
    if fp_region:
        max_fp = max(fp_region, key=lambda x: x[1])
        print(f"  Fingerprint (400-1800): max at {max_fp[0]:.1f} cm⁻¹ = {max_fp[1]:.1f}")
    
    # C-O/C-C region: 800-1200
    co_region = [(rs, intens) for rs, intens in zip(raman_shifts, intensities) if 800 <= rs <= 1200]
    if co_region:
        # Find top 3 in this region
        co_sorted = sorted(co_region, key=lambda x: x[1], reverse=True)
        print(f"  C-O/C-C (800-1200): top peaks at ", end="")
        for rs, intens in co_sorted[:3]:
            print(f"{rs:.1f}({intens:.0f}) ", end="")
        print()
    
    # Low frequency region near Rayleigh: 0-200
    low_region = [(rs, intens) for rs, intens in zip(raman_shifts, intensities) if 0 <= rs <= 200]
    if low_region:
        max_low = max(low_region, key=lambda x: x[1])
        print(f"  Low freq (0-200): max at {max_low[0]:.1f} cm⁻¹ = {max_low[1]:.1f}")
