import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import ntpath
import iesve

class ProjectNotFoundError(AssertionError):
    pass

class FileNotSelectedError(AssertionError):
    pass
    
class IesFilePicker:
    """
    Provides utility functions for getting file/folder paths. To be
    extended/improved as required by the sample scripts. Mostly useful
    for testing out scripts without building a specialised file-picking UI.
    """
    @staticmethod
    def pick_aps_file(title="Select an APS file"):
        """
        Opens  an APS file picker in the current project's vista folder (or in
        the project root if the vista folder doesn't exist yet.)
        Args:
            title (Optional[str]): Title for file picking dialog
        Returns:
            str: full path of selected APS file
        Raises:
            AssertionError: when no file is selected by user
        """
        return IesFilePicker.pick_vista_file([("APS files", "*.aps")], title)
        
    @staticmethod
    def pick_asp_file(title="Select an ASP file"):
        """
        Opens  an ASP file picker in the current project's vista folder (or in
        the project root if the vista folder doesn't exist yet.)
        Args:
            title (Optional[str]): Title for file picking dialog
        Returns:
            str: full path of selected ASP file
        Raises:
            AssertionError: when no file is selected by user
        """
        return IesFilePicker.pick_vista_file([("ASP files", "*.asp")], title)

    @staticmethod
    def pick_apm_file(title="Select an APM file"):
        """
        Opens an APM file picker in the current project's vista folder (or in
        the project root if the vista folder doesn't exist yet.)
        Args:
            title (Optional[str]): Title for file picking dialog
        Returns:
            str: full path of selected APM file
        Raises:
            AssertionError: when no file is selected by user
        """
        return IesFilePicker.pick_vista_file([("APM files", "*.apm")], title)
    
    @staticmethod
    def pick_weather_file():
        """
        Opens a file picker in the users shared content folder
        Args:
            title (Optional[str]): Title for file picking dialog
        Returns:
            str: full path of selected weather file
        Raises:
            AssertionError: when no file is selected by user
        """
        return IesFilePicker.pick_wea_file([("Weather Files", "*.epw;*fwt")], "Pick Weather file")

    @staticmethod
    def pick_vista_file(file_types, title):
        """
        Opens a file picker in the current project's vista folder (or in
        the project root if the vista folder doesn't exist yet.)
        Args:
            file_types (list of tuples): tuples defining sought file types
            title (str): title for file picking dialog
        Returns:
            str: full path of selected file
        Raises:
            AssertionError: when no file is selected by user
        """
        current_project = iesve.VEProject.get_current_project()
        initial_dir = current_project.path
        if not os.path.exists(initial_dir):
            raise ProjectNotFoundError("No IESVE project folder found.")
        vista_dir = initial_dir + "\\vista"
        if os.path.exists(vista_dir):
            initial_dir = vista_dir

        self_dir = os.path.dirname(__file__)
        icon_path = os.path.join(self_dir, 'ies_icon.ico')

        root = Tk()
        root.iconbitmap(icon_path)
        root.withdraw()
        options = {}
        options['initialdir'] = initial_dir
        options['filetypes'] = file_types
        options['title'] = title
        options['parent'] = root
        file_name = askopenfilename(**options)
        root.destroy()

        if not file_name:
            raise FileNotSelectedError("No file selected.")
        return file_name

    @staticmethod
    def pick_wea_file(file_types, title):
        data_path = iesve.get_shared_content_path()
        weather_directory = os.path.join(data_path, "Weather")
        if not os.path.exists(weather_directory):
            raise FileExistsError("no weather files folder found.")
        self_dir = os.path.dirname(__file__)
        icon_path = os.path.join(self_dir, 'ies_icon.ico')

        root = Tk()
        root.iconbitmap(icon_path)
        root.withdraw()
        options = {}
        options['initialdir'] = weather_directory
        options['filetypes'] = file_types
        options['title'] = title
        options['parent'] = root
        file_name = askopenfilename(**options)
        root.destroy()

        if not file_name:
            raise FileNotSelectedError("No file selected.")
        return ntpath.normpath(file_name)

# Example usage
if __name__ == "__main__":
    # APS picker
    file_aps = IesFilePicker.pick_aps_file()
    print("Chosen APS file:", file_aps)
    
    # ASP picker
    file_asp = IesFilePicker.pick_asp_file()
    print("Chosen ASP file:", file_asp)

    # APM picker
    file_apm = IesFilePicker.pick_apm_file()
    print("Chosen APM file:", file_apm)

    # Custom - allow switching between APS/APM selection
    file_c1 = IesFilePicker.pick_vista_file([("APM files", "*.apm"), ("APS files", "*.aps")], "Pick an APS or APM file")
    print("Chosen file (1):", file_c1)

    # Custom = Show APM and APM files all together
    file_c2 = IesFilePicker.pick_vista_file([("APS or APM files", "*.aps;*.apm")], "Pick an APS or APM file")
    print("Chosen file (2):", file_c2)

    weather_file = IesFilePicker.pick_weather_file()
    print("Chosen weather file: ", weather_file)
