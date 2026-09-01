import sys
import numpy as np
from scipy import signal as sp_signal

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QDoubleSpinBox, QSpinBox, QPushButton,
    QGroupBox, QFrame, QSplitter, QScrollArea, QTextBrowser,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# -------------------------------------------------------------------------
# Custom Dark Laboratory Styling (CSS)
# -------------------------------------------------------------------------
DARK_STYLE = """
QMainWindow {
    background-color: #0D1117;
}
QWidget {
    color: #C9D1D9;
    font-family: "Segoe UI", "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 11px;
}
QGroupBox {
    border: 1px solid #21262D;
    border-radius: 6px;
    margin-top: 10px;
    font-weight: bold;
    color: #58A6FF;
    background-color: #161B22;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 8px;
    background-color: #161B22;
    border-radius: 3px;
}
QLabel {
    color: #8B949E;
}
QDoubleSpinBox, QSpinBox {
    background-color: #0D1117;
    border: 1px solid #30363D;
    border-radius: 4px;
    padding: 4px 6px;
    color: #58A6FF;
    font-weight: bold;
}
QDoubleSpinBox:focus, QSpinBox:focus {
    border: 1px solid #58A6FF;
}
QPushButton {
    background-color: #21262D;
    border: 1px solid #30363D;
    border-radius: 4px;
    color: #C9D1D9;
    font-weight: bold;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #30363D;
    border-color: #58A6FF;
    color: #58A6FF;
}
QPushButton#actionBtn {
    background-color: #238636;
    border-color: #2E9E44;
    color: #FFFFFF;
}
QPushButton#actionBtn:hover {
    background-color: #2EA043;
    border-color: #3FB950;
}
QFrame#metricCard {
    background-color: #0D1117;
    border: 1px solid #21262D;
    border-radius: 6px;
}
QTextBrowser {
    background-color: #0D1117;
    border: 1px solid #21262D;
    border-radius: 4px;
    color: #C9D1D9;
    padding: 6px;
}
"""

# -------------------------------------------------------------------------
# Acoustic Parameters Theoretical Reference Text
# -------------------------------------------------------------------------
THEORY_HTML = """
<style>
    body { font-family: sans-serif; font-size: 11px; color: #C9D1D9; line-height: 1.35; }
    h3 { color: #58A6FF; margin-top: 4px; margin-bottom: 4px; font-size: 12px; }
    b { color: #F0883E; }
    code { color: #79C0FF; background-color: #161B22; padding: 1px 3px; border-radius: 3px; }
</style>
<h3>1. Reverberation Parameters (RT60 & EDT)</h3>
<b>RT60 (Reverberation Time):</b> Time required for acoustic energy to decay by <b>60 dB</b> after sound source stops. Extrapolated from -5 dB to -35 dB decay range (T30 line).
<br>
<b>EDT (Early Decay Time):</b> Extrapolated decay time based on initial <b>0 dB to -10 dB</b> range. Directly dictates human perception of room reverberance.

<h3>2. Acoustic Clarity Ratios (C50 & C80)</h3>
Energy ratio comparing early arriving energy to late reverberant tail energy:
<br>
<code>C_t = 10 · log10 [ ∫₀ᵗ h²(τ) dτ / ∫ₜ<sup>∞</sup> h²(τ) dτ ]</code>
<br>
<b>C50 (Speech Clarity, t = 50ms):</b> Values > 0 dB indicate clear speech intelligibility.
<br>
<b>C80 (Music Clarity, t = 80ms):</b> Values between -2 dB and +2 dB represent ideal orchestral balance.

<h3>3. Energy Decay & Schroeder Integration</h3>
Obtained via backwards integration of squared impulse response <code>h(t)</code>:
<br>
<code>E(t) = ∫ₜ<sup>∞</sup> h²(τ) dτ</code>
<br>
Yields a smooth, monotonic Energy Decay Curve (EDC) eliminating stochastic noise fluctuations.
"""

# -------------------------------------------------------------------------
# Main Application GUI Class
# -------------------------------------------------------------------------
class AcousticImpulseAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Acoustic Impulse Response Analyzer")
        self.resize(1380, 880)
        self.setMinimumSize(1024, 720)

        # DSP Setup
        self.fs = 44100  # Sampling frequency (Hz)

        # State storage
        self.t = None
        self.rir = None
        self.edc_db = None
        self.early_ref_mask = None
        self.peak_idx = 0

        self.init_ui()
        self.process_pipeline()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # =================================---------------------------------
        # LEFT PANEL: Parameters, Export & Educational Reference
        # =================================---------------------------------
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        scroll_content = QWidget()
        ctrl_layout = QVBoxLayout(scroll_content)

        # 1. Room Geometry & Acoustic Controls
        group_room = QGroupBox("1. ROOM & SIMULATION PARAMETERS")
        grid_room = QGridLayout(group_room)
        grid_room.setSpacing(6)

        grid_room.addWidget(QLabel("Room Size (m):"), 0, 0)
        self.spin_room_size = QDoubleSpinBox()
        self.spin_room_size.setRange(3.0, 50.0)
        self.spin_room_size.setValue(12.0)
        grid_room.addWidget(self.spin_room_size, 0, 1)

        grid_room.addWidget(QLabel("Speed of Sound (m/s):"), 1, 0)
        self.spin_c = QDoubleSpinBox()
        self.spin_c.setRange(300.0, 360.0)
        self.spin_c.setValue(343.0)
        grid_room.addWidget(self.spin_c, 1, 1)

        grid_room.addWidget(QLabel("Reflection Density:"), 2, 0)
        self.spin_density = QSpinBox()
        self.spin_density.setRange(10, 500)
        self.spin_density.setValue(120)
        grid_room.addWidget(self.spin_density, 2, 1)

        grid_room.addWidget(QLabel("Absorption Coeff (α):"), 3, 0)
        self.spin_abs = QDoubleSpinBox()
        self.spin_abs.setRange(0.05, 0.95)
        self.spin_abs.setValue(0.25)
        self.spin_abs.setSingleStep(0.05)
        grid_room.addWidget(self.spin_abs, 3, 1)

        grid_room.addWidget(QLabel("Reverb Time T60 (s):"), 4, 0)
        self.spin_t60 = QDoubleSpinBox()
        self.spin_t60.setRange(0.1, 5.0)
        self.spin_t60.setValue(1.2)
        self.spin_t60.setSingleStep(0.1)
        grid_room.addWidget(self.spin_t60, 4, 1)

        grid_room.addWidget(QLabel("Noise Floor Level (dB):"), 5, 0)
        self.spin_noise_db = QDoubleSpinBox()
        self.spin_noise_db.setRange(-100.0, -20.0)
        self.spin_noise_db.setValue(-60.0)
        grid_room.addWidget(self.spin_noise_db, 5, 1)

        ctrl_layout.addWidget(group_room)

        # 2. Export Button
        self.btn_export = QPushButton("Export Impulse Response (.csv)")
        self.btn_export.setObjectName("actionBtn")
        self.btn_export.clicked.connect(self.export_csv)
        ctrl_layout.addWidget(self.btn_export)

        # 3. Side Information Panel (Acoustic Explanation)
        group_edu = QGroupBox("ACOUSTIC PARAMETER EXPLANATIONS")
        layout_edu = QVBoxLayout(group_edu)
        edu_browser = QTextBrowser()
        edu_browser.setHtml(THEORY_HTML)
        edu_browser.setFixedHeight(220)
        layout_edu.addWidget(edu_browser)

        ctrl_layout.addWidget(group_edu)
        ctrl_layout.addStretch()

        scroll.setWidget(scroll_content)
        left_layout.addWidget(scroll)

        # Event Signals
        for spin in [self.spin_room_size, self.spin_c, self.spin_density,
                     self.spin_abs, self.spin_t60, self.spin_noise_db]:
            spin.valueChanged.connect(self.process_pipeline)

        # =================================---------------------------------
        # RIGHT PANEL: Measured Metrics Grid & Visual Displays
        # =================================---------------------------------
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Status Banner
        self.lbl_status = QLabel("SYSTEM STATUS: Acoustic Model Active")
        self.lbl_status.setStyleSheet(
            "background-color: #0D1117; color: #3FB950; font-weight: bold; "
            "padding: 6px; border-radius: 4px; border: 1px solid #21262D;"
        )
        right_layout.addWidget(self.lbl_status)

        # Measured Analytics Grid
        metrics_group = QGroupBox("MEASURED ROOM ACOUSTIC INDICATORS")
        grid_metrics = QGridLayout(metrics_group)
        grid_metrics.setSpacing(6)

        self.lbl_rt60 = self.create_metric_card("RT60 (T30 Extrapolated)", "0.00 s", grid_metrics, 0, 0)
        self.lbl_edt = self.create_metric_card("EDT (Early Decay)", "0.00 s", grid_metrics, 0, 1)
        self.lbl_slope = self.create_metric_card("Decay Slope", "0.0 dB/s", grid_metrics, 0, 2)

        self.lbl_c50 = self.create_metric_card("C50 (Speech Clarity)", "0.00 dB", grid_metrics, 1, 0)
        self.lbl_c80 = self.create_metric_card("C80 (Music Clarity)", "0.00 dB", grid_metrics, 1, 1)
        self.lbl_peak_t = self.create_metric_card("Peak Arrival Time", "0.00 ms", grid_metrics, 1, 2)

        right_layout.addWidget(metrics_group)

        # Matplotlib Visualization Canvas
        plots_group = QGroupBox("IMPULSE RESPONSE, ENERGIES & FREQUENCY SPECTRUM")
        layout_plots = QVBoxLayout(plots_group)

        self.fig = Figure(figsize=(9, 7), facecolor='#161B22')
        self.canvas = FigureCanvas(self.fig)
        layout_plots.addWidget(self.canvas)

        right_layout.addWidget(plots_group, stretch=1)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([380, 960])

    def create_metric_card(self, title, default_val, layout, row, col):
        card = QFrame()
        card.setObjectName("metricCard")
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(6, 4, 6, 4)

        lbl_title = QLabel(title.upper())
        lbl_title.setStyleSheet("color: #8B949E; font-size: 10px; font-weight: bold;")
        lbl_val = QLabel(default_val)
        lbl_val.setStyleSheet("color: #58A6FF; font-size: 13px; font-weight: bold;")

        vbox.addWidget(lbl_title)
        vbox.addWidget(lbl_val)
        layout.addWidget(card, row, col)
        return lbl_val

    def generate_synthetic_rir(self):
        """Generates stochastic multi-component Room Impulse Response (RIR)."""
        np.random.seed(42)  # Fixed seed for static reproducibility

        t60_target = self.spin_t60.value()
        duration = max(1.5, t60_target * 1.3)
        num_samples = int(self.fs * duration)
        self.t = np.linspace(0, duration, num_samples, endpoint=False)

        room_size = self.spin_room_size.value()
        c = self.spin_c.value()
        alpha = self.spin_abs.value()
        reflect_coeff = np.sqrt(1.0 - alpha)

        # 1. Direct Sound Component
        direct_delay_s = room_size / c
        self.peak_idx = int(direct_delay_s * self.fs)

        rir = np.zeros(num_samples)
        if self.peak_idx < num_samples:
            rir[self.peak_idx] = 1.0  # Normalized peak

        # 2. Early Reflections (Discrete sparse spikes)
        num_early = 18
        early_window_s = 0.08  # 80ms window
        early_end_idx = self.peak_idx + int(early_window_s * self.fs)

        self.early_ref_mask = np.zeros(num_samples, dtype=bool)

        if early_end_idx < num_samples:
            early_indices = np.random.randint(self.peak_idx + 1, early_end_idx, num_early)
            for idx in early_indices:
                dist_factor = 1.0 + (idx - self.peak_idx) / (0.02 * self.fs)
                amp = (reflect_coeff ** 2) / dist_factor * np.random.choice([-1, 1])
                rir[idx] += amp
                self.early_ref_mask[idx] = True

        # 3. Exponential Late Reverberant Tail (Poisson/Gaussian noise process)
        tau = t60_target / (3.0 * np.log(10))  # Decay rate for 60 dB drop
        decay_envelope = np.zeros(num_samples)

        tail_start_idx = self.peak_idx + 1
        tail_time = self.t[tail_start_idx:] - direct_delay_s
        decay_envelope[tail_start_idx:] = np.exp(-tail_time / tau)

        density = self.spin_density.value()
        late_noise = np.random.normal(0, 0.08, num_samples) * (density / 100.0)
        late_tail = late_noise * decay_envelope * reflect_coeff

        rir += late_tail

        # 4. Add Low-Level Background Noise Floor
        noise_level_amp = 10.0 ** (self.spin_noise_db.value() / 20.0)
        background_noise = np.random.normal(0, noise_level_amp, num_samples)
        rir += background_noise

        self.rir = rir

    def compute_acoustic_metrics(self):
        """Calculates RT60, EDT, C50, C80, Peak Arrival Time, and Decay Slope using Schroeder Integration."""
        h2 = self.rir ** 2

        # Backward Schroeder Integration
        schroeder = np.flip(np.cumsum(np.flip(h2)))
        max_e = max(1e-12, schroeder[0])
        self.edc_db = 10 * np.log10(np.maximum(1e-12, schroeder / max_e))

        t_peak = self.t[self.peak_idx]
        t_rel = self.t - t_peak

        # 1. C50 & C80 Clarity Metrics
        idx_50ms = self.peak_idx + int(0.050 * self.fs)
        idx_80ms = self.peak_idx + int(0.080 * self.fs)

        e_early_50 = np.sum(h2[self.peak_idx:idx_50ms])
        e_late_50 = np.sum(h2[idx_50ms:])
        c50 = 10 * np.log10(e_early_50 / max(1e-12, e_late_50))

        e_early_80 = np.sum(h2[self.peak_idx:idx_80ms])
        e_late_80 = np.sum(h2[idx_80ms:])
        c80 = 10 * np.log10(e_early_80 / max(1e-12, e_late_80))

        # 2. EDT (Early Decay Time: 0 to -10 dB)
        edt = self.fit_decay_range(0.0, -10.0, factor=6.0)

        # 3. RT60 (T30 Extrapolated Range: -5 to -35 dB)
        rt60 = self.fit_decay_range(-5.0, -35.0, factor=2.0)

        # 4. Decay Slope (dB/s)
        decay_slope = -60.0 / rt60 if rt60 > 0 else 0.0

        # Update Metrics UI
        self.lbl_rt60.setText(f"{rt60:.2f} s")
        self.lbl_edt.setText(f"{edt:.2f} s")
        self.lbl_slope.setText(f"{decay_slope:.1f} dB/s")

        self.lbl_c50.setText(f"{c50:+.2f} dB")
        self.lbl_c80.setText(f"{c80:+.2f} dB")
        self.lbl_peak_t.setText(f"{t_peak * 1000.0:.2f} ms")

    def fit_decay_range(self, start_db, end_db, factor=1.0):
        """Fits linear regression line to Schroeder curve across specified dB range."""
        valid_indices = np.where((self.edc_db <= start_db) & (self.edc_db >= end_db))[0]
        if len(valid_indices) < 10:
            return 0.0

        t_sub = self.t[valid_indices]
        edc_sub = self.edc_db[valid_indices]

        # Linear regression slope line
        poly = np.polyfit(t_sub, edc_sub, 1)
        slope = poly[0]  # dB per second

        if abs(slope) < 1e-4:
            return 0.0

        decay_time = (-60.0 / slope) if slope < 0 else 0.0
        return decay_time

    def process_pipeline(self):
        self.generate_synthetic_rir()
        self.compute_acoustic_metrics()
        self.plot_all()

    def export_csv(self):
        """Exports the generated Room Impulse Response and Schroeder Curve to CSV."""
        if self.rir is None:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Impulse Response Data", "room_impulse_response.csv", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                data = np.column_stack((self.t, self.rir, self.edc_db))
                header = "Time_s,ImpulseResponse_Amplitude,EnergyDecayCurve_dB"
                np.savetxt(file_path, data, delimiter=",", header=header, comments="", fmt="%.6f")
                QMessageBox.information(self, "Export Successful", f"RIR Data exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Could not save file:\n{str(e)}")

    def plot_all(self):
        self.fig.clear()

        grid_c = '#21262D'
        text_c = '#8B949E'

        # 1. Subplot 1: Time-Domain Impulse Response with Direct & Early Markers
        ax1 = self.fig.add_subplot(221)
        ax1.set_facecolor('#0D1117')

        t_ms = self.t * 1000.0
        ax1.plot(t_ms, self.rir, color='#58A6FF', linewidth=0.8, alpha=0.7, label="RIR Signal")

        # Direct sound marker
        t_peak_ms = t_ms[self.peak_idx]
        ax1.plot(t_peak_ms, self.rir[self.peak_idx], 'ro', markersize=5, label="Direct Sound")

        # Early reflections markers
        early_indices = np.where(self.early_ref_mask)[0]
        if len(early_indices) > 0:
            ax1.plot(t_ms[early_indices], self.rir[early_indices], 'g^', markersize=4, label="Early Reflections")

        ax1.set_title("Room Impulse Response h(t)", color='#58A6FF', fontsize=9, fontweight='bold', loc='left')
        ax1.set_xlabel("Time (ms)", color=text_c, fontsize=8)
        ax1.set_ylabel("Amplitude", color=text_c, fontsize=8)
        ax1.tick_params(colors=text_c, labelsize=7)
        ax1.grid(True, linestyle='--', alpha=0.3, color=grid_c)
        ax1.legend(facecolor='#161B22', edgecolor=grid_c, labelcolor=text_c, fontsize=7, loc='upper right')

        # 2. Subplot 2: Energy Decay Curve & Schroeder Integration
        ax2 = self.fig.add_subplot(222)
        ax2.set_facecolor('#0D1117')

        ax2.plot(t_ms, self.edc_db, color='#F0883E', linewidth=1.5, label="Schroeder EDC Curve")
        ax2.axhline(y=-5, color='#8B949E', linestyle=':', alpha=0.5)
        ax2.axhline(y=-35, color='#F85149', linestyle=':', label="T30 Limits (-5 to -35 dB)")

        ax2.set_ylim([-80, 5])
        ax2.set_title("Energy Decay Curve (Schroeder Integration)", color='#F0883E', fontsize=9, fontweight='bold', loc='left')
        ax2.set_xlabel("Time (ms)", color=text_c, fontsize=8)
        ax2.set_ylabel("Energy Decay (dB)", color=text_c, fontsize=8)
        ax2.tick_params(colors=text_c, labelsize=7)
        ax2.grid(True, linestyle='--', alpha=0.3, color=grid_c)
        ax2.legend(facecolor='#161B22', edgecolor=grid_c, labelcolor=text_c, fontsize=7, loc='upper right')

        # 3. Subplot 3: Room Frequency Transfer Function |H(f)|
        ax3 = self.fig.add_subplot(212)
        ax3.set_facecolor('#0D1117')

        N = len(self.rir)
        fft_mag = np.abs(np.fft.rfft(self.rir)) / N
        fft_freqs = np.fft.rfftfreq(N, d=1/self.fs)
        mag_db = 20 * np.log10(np.maximum(1e-4, fft_mag))

        ax3.plot(fft_freqs, mag_db, color='#3FB950', linewidth=1.0, label="Transfer Function |H(f)|")
        ax3.set_xscale('log')
        ax3.set_xlim([20, 20000])

        ax3.set_title("Frequency Response (Room Transfer Function)", color='#3FB950', fontsize=9, fontweight='bold', loc='left')
        ax3.set_xlabel("Frequency (Hz)", color=text_c, fontsize=8)
        ax3.set_ylabel("Magnitude (dB)", color=text_c, fontsize=8)
        ax3.tick_params(colors=text_c, labelsize=7)
        ax3.grid(True, which='both', linestyle='--', alpha=0.3, color=grid_c)
        ax3.legend(facecolor='#161B22', edgecolor=grid_c, labelcolor=text_c, fontsize=7, loc='upper right')

        for ax in [ax1, ax2, ax3]:
            for spine in ax.spines.values():
                spine.set_color(grid_c)

        self.fig.tight_layout()
        self.canvas.draw()


# -------------------------------------------------------------------------
# Entry Point
# -------------------------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(DARK_STYLE)

    window = AcousticImpulseAnalyzerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()