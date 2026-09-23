import json

from bs4 import BeautifulSoup

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

    def readFeaReports(self, filesPaths:list[str]) ->list[str]:

        for path in filesPaths:
            with open(path, "r", encoding="utf-8") as file:
                html = file.read()
                result = self.parse_tables(html, self.tables_to_extract)
                jsonOutput =  json.dumps(result, indent=4,ensure_ascii=False)

                #TODO Its okay, then we need to parse scenes and photos


            file = open(path)
            soupDoc = BeautifulSoup(file, "lxml")

            reportId = soupDoc.select_one('h2:nth-of-type(3)')
            docAllTables = soupDoc.select('h2:nth-of-type(3) ~ table')


            #########
            productMatherialTable = self._convertSeveralRowsTableToJson(docAllTables[1], "Material")
            gasMatherialTable = self._convertSeveralRowsTableToJson(docAllTables[2], "Gas Material")

            ##########
            fidelityElement = soupDoc.find('h3', string="Fidelity")
            fidelityTable = fidelityElement.find_next('table')

            convertedFidelityTable = self._convertSeveralRowsColumsTableToJson(fidelityTable, "Fidelity table")

            #########
            flowInletsElement = soupDoc.find(string="Flow Inlets")
            flowInletsTable = flowInletsElement.find_next('table')

            convertedFlowInletsTable = self._convertSeveralRowsColumsTableToJson(fidelityTable, "Flow Inlets")


            #for card in soup.select("div.job-card"):
            #title_el = card.select_one("h2.title a")


        '''
        class FeaReportInstance:
        reportTitle:str
        reportDate:str
        simulationSettings:str
        pythicsConditions:str
        monitorsData:str
        sceneInstances:list[ReportSceneInstance]'''

        return list["Ok"]

    def _convertSeveralRowsColumsTableToJson(self, htmTable, tableTitle:str) -> object :
        data = []

        row = {"Title": tableTitle}
        data.append(dict(Table = row))

        rows = htmTable.find_all('tr')
        headers = [th.get_text(strip=True) for th in rows[0].find_all('th')]

        for row in rows[1:]:
            cells = row.find_all('td')
            if not cells:
                continue
            values = [td.get_text(strip=True) for td in cells]
            data.append(dict(zip(headers, values)))

        formatedTable = json.dumps(data, indent=2, ensure_ascii=False)
        return formatedTable

    def _convertSeveralRowsTableToJson(self, htmTable, tableTitle:str) -> object :
        result = {}
        result["Table"] = tableTitle

        for row in htmTable.select('tr'):
            th = row.find('th')
            td = row.find('td')

            if th and td:
                rowName = th.get_text(strip=True)
                if rowName == "Description":
                    rowData = td.get_text().splitlines()[0]
                    result[rowName] = rowData
                else:
                    key = rowName
                    value = td.get_text(strip=True)
                    result[key] = value

        formatedTable = json.dumps(result, indent=2, ensure_ascii=False)
        return formatedTable


    def parse_table(self, table):
        """
        Parse one HTML table.

        Supports:

        1. Key/value tables

            <th>Name</th>
            <td>Steel</td>

        2. Normal tables

            <th>Name</th>
            <th>Type</th>

            <td>Setting 1</td>
            <td>Body</td>
        """

        rows = table.find_all("tr")

        if not rows:
            return []

        # --------------------------------------------------------
        # Detect key/value table
        # --------------------------------------------------------

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

        # --------------------------------------------------------
        # Normal table
        # --------------------------------------------------------

        header_row = next(
        (row for row in rows if row.find("th")),
        None
    )

        if header_row is None:
            return []

        headers = [
            cell.get_text(" ", strip=True)
            for cell in header_row.find_all(["th", "td"])
        ]

        result = []

        for row in rows:

            if row is header_row:
                continue

            cells = row.find_all(["td", "th"])

            if not cells:
                continue

            values = [
                cell.get_text(" ", strip=True)
                for cell in cells
            ]

            row_data = {}

            for index, header in enumerate(headers):

                row_data[header] = (
                    values[index]
                    if index < len(values)
                    else None
                )

            result.append(row_data)

        return result


    # ============================================================
    # Parse Monitors
    # ============================================================

    def parse_monitors(self, heading):
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
            }
        """

        monitors = {}
        section_level = int(heading.name[1])
        current_monitor = None
        for element in heading.find_all_next():

                # ----------------------------------------------------
                # Stop at next section of same/higher level
                # ----------------------------------------------------

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

                # ------------------------------------------------
                # New monitor
                # ------------------------------------------------

                if level == section_level + 1:

                    current_monitor = (
                        element.get_text(" ", strip=True)
                    )

            # ----------------------------------------------------
            # Table belonging to current monitor
            # ----------------------------------------------------

            elif (
                    element.name == "table"
                    and current_monitor is not None
            ):

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

                # ------------------------------------------------
                # Convert columns into:
                #
                # {
                #     "Refine": {
                #         "Pressure Drop": "31,9 Pa"
                #     }
                # }
                # ------------------------------------------------

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


    # ============================================================
    # Main parser
    # ============================================================

    def parse_tables(self, html:str, tables_to_extract:list[str]):

        soup = BeautifulSoup(html, "html.parser")
        output = {}

        # ---------------------------------------------------------
        # Report Id
        # ---------------------------------------------------------

        report_id = None

        output["Report Id"] = self._found_report_id(soup)


        for requested_name in tables_to_extract:
            # ----------------------------------------------------
            # Find section
            # ----------------------------------------------------

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

            # ----------------------------------------------------
            # Special case: Monitors
            # ----------------------------------------------------

            if requested_name.lower() == "monitors":

                output[requested_name] = self.parse_monitors(
                    heading
                )

                continue

            # ----------------------------------------------------
            # Generic section
            # ----------------------------------------------------

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
                        self.parse_table(element)
                    )

            output[requested_name] = tables
        return output


    def _found_report_id(self, soupData)->str:
        # Report Id is always stored in the <h2> immediately
        # after the Geometry section.

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
