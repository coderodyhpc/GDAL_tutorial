from typing import List, Callable
from threading import Timer
import time

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QWidget, QDockWidget, QTabWidget

from qgis.core import QgsCoordinateReferenceSystem, QgsMessageLog, Qgis, QgsProject, QgsLayerTree, QgsRasterLayer
from qgis.gui import QgisInterface

class TabulaDock(QDockWidget):
    def __init__(self, iface: QgisInterface, dock_widget: QDockWidget) -> None:   
        super().__init__('TABULA')
#_____ TABS SET UP _____#
        tabs = QTabWidget()
        tabs.setStyleSheet('''QTabBar::tab {font-size: 10pt; font-family: Verdana; font-weight: bold; color: #004F00; height: 40px; width: 140px;}''')
        self.tab1 = QWidget()
        tabs.addTab(self.tab1,"TAB 1")
        self.tab2 = QWidget()
        tabs.addTab(self.tab2,"TAB 2")
#        tabs.addTab(WhiteScroll(CMAQHomeTab()), 'CMAQ')
        self.setWidget(tabs)
        self.tabs = tabs
        self.add_stamen_basemap()
#        self.add_naip_basemap()
        
    def add_stamen_basemap(self):
        print ("Adding Stamen")
        url = 'type=xyz&zmin=0&zmax=20&url=http://a.tile.stamen.com/terrain-background/{z}/{x}/{y}.png'
        attribution = 'Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL'
        attribution_url = 'http://maps.stamen.com'
        registry = QgsProject.instance() # type: QgsProject
        root = registry.layerTreeRoot() # type: QgsLayerTree

        tree_layers = filter(QgsLayerTree.isLayer, root.children())
        if any(tree_layer.layer().source() == url for tree_layer in tree_layers):
            return
        layer = QgsRasterLayer(url, 'Stamen Terrain Background', 'wms')
        layer.setAttribution(attribution)
        layer.setAttributionUrl(attribution_url)
        registry.addMapLayer(layer, False)
        root.addLayer(layer)

    # Reset the Project CRS to WGS84 otherwise it will be set to the stamen layer CRS
        def setWGS84():
            registry.setCrs((QgsCoordinateReferenceSystem.fromProj4("+proj=longlat +datum=WGS84 +no_defs")))
        setWGS84()
    # Again with a delay, which is a work-around as sometimes QGIS does not apply the CRS change above.
        Timer(0.5, setWGS84).start()

    def add_naip_basemap(self):
        url = 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/0/0/0'
        print ('AT NAIP ',url) 
##    attribution = 'Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL'
##    attribution_url = 'http://maps.stamen.com'
        registry = QgsProject.instance() # type: QgsProject
        root = registry.layerTreeRoot() # type: QgsLayerTree

        tree_layers = filter(QgsLayerTree.isLayer, root.children())
        if any(tree_layer.layer().source() == url for tree_layer in tree_layers):
            return
        layer = QgsRasterLayer(url, 'NAIP', 'wms')
##    layer.setAttribution(attribution)
##    layer.setAttributionUrl(attribution_url)
        registry.addMapLayer(layer, False)
    #    root.addLayer(layer)

    # Reset the Project CRS to WGS84 otherwise it will be set to the stamen layer CRS
        def setWGS84():
            registry.setCrs((QgsCoordinateReferenceSystem.fromProj4("+proj=longlat +datum=WGS84 +no_defs")))
        setWGS84()
#    # Again with a delay, which is a work-around as sometimes QGIS does not apply the CRS change above.
        Timer(0.5, setWGS84).start()    
        
#__ Initialization of the graphic environment ___#
class QGISPlugin():
    def __init__(self, iface: QgisInterface) -> None:
        self.iface = iface
        self.actions = []  # type: List[QAction]
        self.dock_widget = None # type: WrfDock
        
    def initGui(self) -> None:
        """Create the menu entries and toolbar icons inside the QGIS GUI.
           Note: This method is called by QGIS.
        """

#        install_user_error_handler(self.iface) #This is at plugin/ui/helpers.py
#___ These are the actions defining the different options at the Gv3GEWRF menu 
#___ (maybe I should get rid of it and simply start the app w/o asking any Qs) 
        self.menu = '&' + 'TABULA'
        self.add_action(icon_path='/home/ubuntu/.local/share/QGIS/QGIS3/profiles/default/python/plugins/TABULA/logo16B.png',
                        text="TABULA", callback=self.show_dock, add_to_toolbar=True,
                        parent=self.iface.mainWindow(), status_tip='Testing TABULA')

#__ I believe that this might be to set up the Settings/options ___#
#        self.options_factory = OptionsFactory() # This is at gis4wrf/plugin/ui/options.py
#        self.iface.registerOptionsWidgetFactory(self.options_factory)
#        self.options = get_options()

#        self.check_versions() #I'm deactivating check_versions - probably needs to be erased

    def unload(self) -> None:
        """Removes the plugin menu item and icon from QGIS GUI.
           Note: This method is called by QGIS.
        """
        pass

#__ Functions  ___#
    def show_dock(self) -> None:
        if not self.dock_widget:
            self.dock_widget = TabulaDock(self.iface, self.dock_widget)
#! What happens if I change Right with Left
        self.iface.addDockWidget(
            Qt.RightDockWidgetArea, self.dock_widget)
#        add_default_basemap()
#        add_naip_basemap()
#        self.dock_widget.hasFocus.connect(self.on_dock_focus)
#        self.iface.addWidget(
#            self.dock_widget)

    def add_action(self, icon_path: str, text: str, callback: Callable,
                   enabled_flag: bool=True, add_to_menu: bool=True,
                   add_to_toolbar: bool=False, add_to_add_layer: bool=False,
                   status_tip: str=None, whats_this: str=None, parent: QWidget=None
                   ) -> QAction:
        """Helper function for creating menu items
        Parameters
        ----------
        icon_path: Path to the icon for this action. Can be a resource
            path (e.g. `:/plugins/foo/bar.png`) or a normal file system path.
        text: Text that should be shown in menu items for this action.
        callback: Function to be called when the action is triggered.
        enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        add_to_toolbar: Flag indicating whether the action should also
            be added to the Plugins toolbar. Defaults to False.
        add_to_layer: Flag indicating whether the action should also
            be added to the Layer > Add Layer menu. Defaults to False.
        status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action after clicking on `?`.
        parent: Parent widget for the new action. Defaults None.
        Returns
        -------
        out: The action that was created. Note that the action is
            also added to `self.actions` list.
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        if add_to_add_layer:
            self.iface.insertAddLayerAction(action)

        self.actions.append(action)

        return action
    
