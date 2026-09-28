import base64
import json
import os

from pathlib import Path
from bs4 import BeautifulSoup

from App.SupportingData.initalSettings import TEMP_TARGET_FOLDER


class FeaReportsConverter:
    """Parser schema:
        │
        ├── Materials
        │   └── generic table parser
        │
        ├── Fidelity
        │   └── generic table parser
        │
        └── Monitors
        └── special monitor parser
        ├── simulation mode
        │   └── monitor name → value
        └── simulation mode
        └── monitor name → value"""

    def __init__(self):
        self.tables_to_extract = [
            "Materials",
            "Fidelity",
            "Physics Conditions",
            "Monitors"
        ]

    def readFeaReports(self, filesPaths:list[str]) ->list[object]:
        reportsInJson:list[object] = []
        for path in filesPaths:
            with open(path, "r", encoding="utf-8") as file:
                html = file.read()

                file_name = Path(path).stem
                parsedTables = self._parse_tables(file_name, html, self.tables_to_extract)

                #Adding Scenes
                parsedTables["Scenes"] = self._parse_scenes(html, file_name)

                jsonOutput = json.dumps(parsedTables, indent=4,ensure_ascii=False)
                reportsInJson.append(jsonOutput)

        return reportsInJson

    def _parse_report_table(self, table):

        """ Parse one HTML table
       Supports:
       1. Key/value tables
           <th>Name</th>
           <td>Steel</td>

       2. Normal tables
           <th>Name</th>
           <th>Type</th>

           <td>Setting 1</td>
           <td>Body</td>"""

        rows = table.find_all("tr")

        if not rows:
            return []

        # Detect key/value table
        is_key_value_table = all(
            len(row.find_all(["th", "td"])) == 2
            and row.find("th") is not None
            for row in rows
        )

        if is_key_value_table:
            result = {}
            for row in rows:
                cells = row.find_all(["th", "td"])
                key = cells[0].get_text(" ", strip=True)
                value = cells[1].get_text(" ", strip=True)

                result[key] = value

            return [result]

        # Normal table

        header_row = next(
        (row for row in rows if row.find("th")),
        None)

        if header_row is None:
            return []

        headers = [
            cell.get_text(" ", strip=True)
            for cell in header_row.find_all(["th", "td"])]

        result = []

        for row in rows:

            if row is header_row:
                continue

            cells = row.find_all(["td", "th"])

            if not cells:
                continue

            values = [
                cell.get_text(" ", strip=True)
                for cell in cells]

            row_data = {}

            for index, header in enumerate(headers):
                row_data[header] = (
                    values[index]
                    if index < len(values)
                    else None
                )

            result.append(row_data)
        return result

    # Parse Monitors

    def _parse_monitors(self, heading):
        """
        Parse:
            <h3>Monitors</h3>

            <h4>Pressure Drop</h4>
            <table>
                <th>Design</th>
                <th>Refine</th>
                ...
            </table>

        into:
            {
                "Refine": {
                    "Pressure Drop": "31,9 Pa"
                }
            }"""

        monitors = {}
        section_level = int(heading.name[1])
        current_monitor = None

        for element in heading.find_all_next():
            # Stop at next section of same/higher level
            if element.name in {
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6"
            }:
                level = int(element.name[1])
                if level <= section_level:
                    break

                # New monitor
                if level == section_level + 1:
                    current_monitor = (
                        element.get_text(" ", strip=True)
                    )

            # Table belonging to current monitor
            elif (element.name == "table" and current_monitor is not None):
                rows = element.find_all("tr")

                if not rows:
                    continue

                # First row = column names
                header_row = next(
                    (
                        row
                        for row in rows
                        if row.find("th")
                    ),
                    None
                )

                if header_row is None:
                    continue

                headers = [
                    cell.get_text(" ", strip=True)
                    for cell in header_row.find_all(
                        ["th", "td"]
                    )
                ]

                # Find first data row
                data_row = next(
                    (
                        row
                        for row in rows
                        if row is not header_row
                           and row.find_all(["td", "th"])
                    ),
                    None
                )

                if data_row is None:
                    continue

                values = [
                    cell.get_text(" ", strip=True)
                    for cell in data_row.find_all(
                        ["td", "th"]
                    )
                ]
                # Convert columns into:
                #
                # {
                #     "Refine": {
                #         "Pressure Drop": "31,9 Pa"
                #     }
                # }

                for index, header in enumerate(headers):
                    # "Design" is not a simulation mode
                    if header.lower() == "design":
                        continue

                    if index >= len(values):
                        continue

                    value = values[index]

                    if header not in monitors:
                        monitors[header] = {}

                    monitors[header][current_monitor] = value
        return monitors

    # Main parser
    def _parse_tables(self,file_name:str, html:str, tables_to_extract:list[str])->dict:

        soup = BeautifulSoup(html, "html.parser")
        output = {}

        # Report source name, simulation Id
        output["Source file"] = file_name
        output["Report Id"] = self._found_report_id(soup)

        for requested_name in tables_to_extract:
            # Find section

            heading = soup.find(
                lambda tag:
                tag.name in {
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6"
                }
                and tag.get_text(strip=True).lower()
                == requested_name.lower()
            )

            if heading is None:
                output[requested_name] = []
                continue

            # Special case: Monitors
            if requested_name.lower() == "monitors":
                output[requested_name] = self._parse_monitors(
                    heading
                )
                continue

            # Generic section

            section_level = int(heading.name[1])
            tables = []
            for element in heading.find_all_next():

                # Stop at next section
                if element.name in {
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6"
                }:
                    element_level = int(element.name[1])
                    if element_level <= section_level:
                        break

                # Extract table
                if element.name == "table":

                    tables.append(
                        self._parse_report_table(element)
                    )

            output[requested_name] = tables
        return output

    def _found_report_id(self, soupData)->str:
        # Report Id is always stored in the <h2> immediately
        # after the Geometry section
        id  = ""

        geometry_heading = None

        for h in soupData.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            if h.get_text(" ", strip=True).lower() == "geometry":
                geometry_heading = h
                break

        if geometry_heading:
            for element in geometry_heading.find_all_next(["h1", "h2", "h3", "h4", "h5", "h6"]):
                if element.name == "h2":
                    id = element.get_text(" ", strip=True)
                    break
        return id

    def _parse_scenes(self, html:str, simulationTitle:str)->list:
        soup = BeautifulSoup(html, "html.parser")

        saved_scenes = []
        # Find the "Saved Scenes" section
        heading = soup.find("h3", string=lambda s: s and s.strip() == "Saved Scenes")

        if not heading:
            return saved_scenes

        # Everything until the next h3
        for element in heading.find_all_next():
            if element.name == "h3" and element is not heading:
                break

            if element.name == "h4":
                sceneName = element.get_text()

                # The scene image
                img = element.find_next("img", class_="saved-scene")
                imgData = img.get("src") if img else None

                savedImgPath = self._saveBase64Img(imgData, simulationTitle, sceneName, TEMP_TARGET_FOLDER)

                clearImgPath = savedImgPath.replace("\\", "/")
                formatedPath = f"file:///{clearImgPath}"

                scene = {
                    "Scene name": sceneName,
                    "src": formatedPath,
                    "alt": sceneName
                }

                saved_scenes.append(scene)
        return saved_scenes

    def _saveBase64Img(self, base64Src:str, simulationName:str, imgFileName:str, targetFolder:str)->str:
        # Ensure folder exists
        os.makedirs(targetFolder, exist_ok=True)

        # Remove "data:image/png;base64," prefix
        if "," in base64Src:
            base64Src = base64Src.split(",", 1)[1]

        image_data = base64.b64decode(base64Src)

        sceneName = imgFileName.split(",", 1)[0]
        fileName = f"{simulationName}_{sceneName}.png"

        fullPath = os.path.join(targetFolder,  fileName)

        with open(fullPath, "wb") as f:
            f.write(image_data)

        return fullPath