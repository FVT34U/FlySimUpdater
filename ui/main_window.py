import dearpygui.dearpygui as dpg
from core import version_checker, updater, game_runner
from config.config import config


logged_messages = []


def update_progress(value):
    dpg.set_value("ProgressBar", value)

def make_logger():
    msg_idx = 0
    def log(text):
        nonlocal msg_idx
        dpg.add_text(text, parent="LogWindow", tag=f"log_{msg_idx}")
        logged_messages.append(f"log_{msg_idx}")
        print(text)
        msg_idx += 1
    return log

log = make_logger()

def clear_log():
    for item in logged_messages:
        dpg.delete_item(item)
    logged_messages.clear()

def check_for_updates(sender, data):
    log("Checking for updates...")
    local_version = version_checker.get_local_version()
    remote_version = version_checker.get_remote_version()

    if not remote_version:
        log("Cannot get version from server, try again later")
        return

    if not local_version:
        local_version = "0.0.0"

    if version_checker.is_update_needed(local_version, remote_version):
        log(f"New version {remote_version} is available. Updating...")
        dpg.show_item("ProgressBar")
        updater.update_game(ui_callback=update_progress)
        log("Update was installed!")
        dpg.set_value("ProgressBar", 0.0)
        dpg.hide_item("ProgressBar")
    else:
        log("You have latest version of FlySim.")

def start_launcher():
    dpg.create_context()

    with dpg.font_registry():
        default_font = dpg.add_font("fonts/TikTokSans16pt-Medium.ttf", 16)
        #second_font = dpg.add_font("fonts/TikTokSans12pt-Regular.ttf", 12)

    with dpg.window(
            label="FlySim Updater",
            tag="MainWindow",
            width=640, height=380,
            no_resize=True,
            no_move=True,
            no_close=True,
            no_collapse=True
        ):
        with dpg.group(horizontal=True):
            with dpg.child_window(tag="UpdaterWindow", width=400, height=300):
                dpg.add_text("FlySim Launcher")
                dpg.add_text("русский")
                dpg.add_spacer()
                dpg.add_button(label="Check for updates", callback=check_for_updates)
                dpg.add_button(label="Launch FlySim", callback=lambda s, d: game_runner.run_game())
                dpg.add_spacer()
                dpg.add_progress_bar(label="ProgressBar", tag="ProgressBar", default_value=0.0, overlay="Progress...", show=False)
            with dpg.child_window(tag="LogWindow", width=200, height=300):
                dpg.add_text("Log:")
                dpg.add_button(label="Clear", callback=clear_log)


    dpg.create_viewport(title="FlySim Launcher", width=700, height=500)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    viewport_width = dpg.get_viewport_width()
    viewport_height = dpg.get_viewport_height()

    window_width = dpg.get_item_width("MainWindow")
    window_height = dpg.get_item_height("MainWindow")

    x = (viewport_width - window_width) // 2
    y = (viewport_height - window_height) // 2

    dpg.set_item_pos("MainWindow", [x, y])

    dpg.start_dearpygui()
    dpg.destroy_context()
