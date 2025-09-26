from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os
import gui
import util
import shutil

class MainWindow(QtWidgets.QMainWindow):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.ui = gui.Ui_MainWindow()
		self.ui.setupUi(self)
		# Backward compatibility alias if code refers to wallLabel while UI defines label
		if not hasattr(self.ui, 'wallLabel') and hasattr(self.ui, 'label'):
			self.ui.wallLabel = self.ui.label

		# Connect buttons to handler methods
		self.ui.get_wall_path_btn.clicked.connect(self.handle_get_wall_path)
		self.ui.extract_wall_btn.clicked.connect(self.handle_extract_wallpaper)

		# Load current wallpaper path
		self._orig_pixmap: QPixmap | None = None
		path = util.get_current_wallpaper_path()

		if isinstance(path, str) and os.path.isfile(path):
			pm = QPixmap(path)
			if not pm.isNull():
				self._orig_pixmap = pm
				self._update_label_pixmap()
				self.ui.get_wall_path_btn.setEnabled(True)
				self.ui.extract_wall_btn.setEnabled(True)
			else:
				# Failed to load pixmap from a given path
				self._show_message("wallLabel", "Failed to load wallpaper image.", f"Failed to load: {path}")
				self.ui.get_wall_path_btn.setEnabled(False)
				self.ui.extract_wall_btn.setEnabled(False)
		else:
			# Invalid or missing path; show message instead of image
			self._show_message("wallLabel", "Wallpaper path invalid or not found.")
			self.ui.get_wall_path_btn.setEnabled(False)
			self.ui.extract_wall_btn.setEnabled(False)

		# Align image to center
		self.ui.wallLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter
							    | Qt.AlignmentFlag.AlignVCenter)
		# Allow shrinking window
		self.ui.wallLabel.setMinimumSize(0, 0)
		self.ui.wallLabel.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored,
								   QtWidgets.QSizePolicy.Policy.Preferred)

	# Scale image to fill 100% of label's width and set it
	def _update_label_pixmap(self):
		if not self._orig_pixmap or self._orig_pixmap.isNull(): return
		label_width = self.ui.wallLabel.width()
		if label_width <= 0: return
		scaled = self._orig_pixmap.scaledToWidth(label_width, Qt.TransformationMode.SmoothTransformation)
		self.ui.wallLabel.setPixmap(scaled)

	# Clear current image and show a message on a target label (default: wallLabel)
	def _show_message(self, label_name, text, tooltip=None):
		self._orig_pixmap = None
		label = getattr(self.ui, label_name, None)
		# Fallback: if requested label not found but 'label' exists
		if label is None and hasattr(self.ui, 'label'):
			label = self.ui.label
		# Cannot find a label
		if label is None:
			return
		label.clear()
		label.setText(text)
		label.setToolTip(tooltip if tooltip is not None else text)

	# Add _update_label_pixmap to the Qt's resizeEvent
	# When resizing the window, make image always fill label's width
	def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
		super().resizeEvent(event)
		self._update_label_pixmap()

	# Add _update_label_pixmap to the Qt's showEvent
	# Ensure initial scaling after the widget has a real size
	def showEvent(self, event: QtGui.QShowEvent) -> None:
		super().showEvent(event)
		QtCore.QTimer.singleShot(0, self._update_label_pixmap)

	# Handle 'Get Current Wallpaper Path' button.
	def handle_get_wall_path(self):
		path = util.get_current_wallpaper_path()
		self._show_message("btn_msg_label", f"File path {path} copied to clipboard.")
		QtWidgets.QApplication.clipboard().setText(path)
		return path

	# Handle 'Extract Wallpaper' button
	def handle_extract_wallpaper(self):
		file_path = util.get_current_wallpaper_path()
		# Validate source path
		if not isinstance(file_path, str) or not os.path.isfile(file_path):
			self._show_message("btn_msg_label", "No valid wallpaper file to extract.")
			return None

		target_dir = os.path.join(os.getcwd(), "img")
		os.makedirs(target_dir, exist_ok=True)

		basename = os.path.basename(file_path)
		name, ext = os.path.splitext(basename)

		# Handles duplicate
		candidate = basename
		counter = 2
		while os.path.exists(os.path.join(target_dir, candidate)):
			candidate = f"{name} ({counter}){ext}"
			counter += 1

		dest_path = os.path.join(target_dir, candidate)
		try:
			shutil.copy2(file_path, dest_path)
			self._show_message("btn_msg_label", f"Extracted to img/{candidate}")
			# print(f"[Extract] Copied wallpaper to {dest_path}")
			# return dest_path
		except Exception as e:
			self._show_message("btn_msg_label", f"Failed to extract: {e}")
			# print(f"[Extract][Error] {e}")
			# return None

def main():
	import sys
	app = QtWidgets.QApplication(sys.argv)

	win = MainWindow()
	win.show()
	sys.exit(app.exec())

if __name__ == "__main__":
	main()