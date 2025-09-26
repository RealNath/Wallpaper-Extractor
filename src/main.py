from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
import os
import shutil

import gui
import util

class MainWindow(QtWidgets.QMainWindow):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.ui = gui.Ui_MainWindow()
		self.ui.setupUi(self)
		# If code refers to wallLabel while UI defines label
		if not hasattr(self.ui, 'wallLabel') and hasattr(self.ui, 'label'):
			self.ui.wallLabel = self.ui.label

		# Connect buttons to handler methods
		self.ui.get_wall_path_btn.clicked.connect(self.handle_get_wall_path)
		self.ui.extract_wall_btn.clicked.connect(self.handle_extract_wallpaper)

		# Default state
		self._orig_pixmap = None
		self._video_player = None
		self._video_widget = None
		self._audio_output = None

		# Load wallpaper
		path = util.get_current_wallpaper_path()
		path = r"D:\Programs\Wallpaper Extractor\src\test.mp4"

		if isinstance(path, str) and os.path.isfile(path):
			_, ext = os.path.splitext(path)
			# Windows recently added video/live wallpaper for beta
			# I didn't get to use this feature yet
			# Most likely the way to obtain the current vid's path is the same
			if ext.lower() == ".mp4":
				self._setup_video_player(path)
				self._enable_buttons()
			else:
				pm = QPixmap(path)
				if not pm.isNull():
					self._orig_pixmap = pm
					self._update_label_pixmap()
					self._enable_buttons()
				else:
					# Failed to load pixmap from a given path
					self._show_message("wallLabel", "Failed to load wallpaper image.", f"Failed to load: {path}")
					self._enable_button(False)
		else:
			# Invalid or missing path; show message instead of image
			self._show_message("wallLabel", "Wallpaper path invalid or not found.")
			self._enable_button(False)

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

	# Embed a looping, muted video player
	def _setup_video_player(self, path: str):
		# Replace wallLabel with QVideoWidget
		layout = self.ui.verticalLayout
		idx = layout.indexOf(self.ui.wallLabel)
		if idx == -1: idx = 0
		self.ui.wallLabel.hide()
		layout.removeWidget(self.ui.wallLabel)
		self.ui.wallLabel.setParent(None)

		self._video_widget = QVideoWidget(self)
		self._video_widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred,
										 QtWidgets.QSizePolicy.Policy.Expanding)
		self._video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
		layout.insertWidget(idx, self._video_widget)

		self._video_player = QMediaPlayer(self)
		self._audio_output = QAudioOutput(self)
		self._video_player.setAudioOutput(None)
		self._video_player.setVideoOutput(self._video_widget)
		self._video_player.setSource(QtCore.QUrl.fromLocalFile(path))

		# Make it loop, unpausable
		self._video_player.mediaStatusChanged.connect(self._on_media_status)
		self._video_player.playbackStateChanged.connect(self._on_state_changed)
		
		self._video_player.play()

	# Loop after video reaches the end
	def _on_media_status(self, status):
		try:
			if status == QMediaPlayer.MediaStatus.EndOfMedia:
				self._video_player.setPosition(0)
				self._video_player.play()
		except Exception: pass

	# Auto resume if paused or stopped
	def _on_state_changed(self, state):
		try:
			if state != QMediaPlayer.PlaybackState.PlayingState:
				self._video_player.play()
		except Exception: pass


	# Enable/disable buttons
	def _enable_buttons(self, status=True):
		if status:
			self.ui.get_wall_path_btn.setEnabled(True)
			self.ui.extract_wall_btn.setEnabled(True)
		else:
			self.ui.get_wall_path_btn.setEnabled(False)
			self.ui.extract_wall_btn.setEnabled(False)

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