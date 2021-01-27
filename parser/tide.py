class DailyTide():

    def __init__(self, daily_tide_data):
        """
        Daily tide information, include date and four max/min tidal range.

        Params:
            daily_tide_data : list(beautifulsoup html object).

        Example:
          [
            <tr>
              <td headers="date" id="day1" rowspan="4">05/29(五)<br/>農曆 04/07<span class="orange-text">潮差：中</span></td>
              <td headers="day1 tide">滿潮 <i aria-hidden="true" class="icon-cwb-height"></i></td>
              <td headers="day1 time">03:20</td>
              <td headers="day1 Above_TWVD">115</td>
              <td headers="day1 Above_Local_MSL">115</td>
              <td headers="day1 Above_Chart_Datum">270</td>
            </tr>,
            ...
          ]

        """
        self.date_html_info = None
        self.tide_html_info_list = []

        self._parse_data(daily_tide_data)

    def _parse_data(self, daily_tide_data):
        for idx, tide_html in enumerate(daily_tide_data):
            # The first tide data content date info.
            if idx == 0:
                self.date_html_info = tide_html.select("td").pop(0)
            self.tide_html_info_list.append(tide_html)

    def _struct_tide_info(self, tide, time, tidal_range):
        tide_info = {
            "tide": tide,
            "time": time,
            "tidal_range": tidal_range
        }
        return tide_info

    @property
    def date(self):
        return self.date_html_info.contents[0]

    @property
    def date_lunar_calendar(self):
        return self.date_html_info.contents[2]

    @property
    def tidal_range(self):
        return self.date_html_info.contents[3].text

    @property
    def tide_info_list(self):
        """
        Returns:
            list: _struct_tide_info() dictionaries.
        """

        tide_list = []
        for idx, tide_html in enumerate(self.tide_html_info_list):
            offset = 1 if idx == 0 else 0 # The first tide html block has date info, ignore it.
            tide = tide_html.select("td")[0+offset].text
            time = tide_html.select("td")[1+offset].text
            tidal_range = tide_html.select("td")[2+offset].text
            tide_info = self._struct_tide_info(tide, time, tidal_range)
            tide_list.append(tide_info)

        return tide_list


def tide_parser(tide_html):
    """
    Params:
        tide_html : list(beautifulsoup html object).

    Returns:
        list : DailyTide class object.
    """
    header_of_date = "date"

    daily_tide_list = [] # Parsed tide data.
    daily_tide_html_list = []
    month_tide_html_list = tide_html.select("tr")
    for idx, tide in enumerate(month_tide_html_list):
        
        # First one is title of column, ignore it.
        if idx == 0:
            continue

        header_of_tide = tide.select('td')[0].get('headers')[0]
        if header_of_date == header_of_tide:
            if daily_tide_html_list:
                daily_tide_list.append(DailyTide(daily_tide_html_list))
                daily_tide_html_list = [tide]
                continue

        daily_tide_html_list.append(tide)

    if daily_tide_html_list:
        daily_tide_list.append(DailyTide(daily_tide_html_list))

    return daily_tide_list


def _get_sorted_tidal_range(daily_tide_list):
    """ Get the lowest three tidal range."""
    tidal_range_set = set()
    for daily_tide in daily_tide_list:
        for tide in daily_tide.tide_info_list:
            tidal_range_set.add(int(tide["tidal_range"]))

    tidal_range_list = list(tidal_range_set)
    tidal_range_list.sort(reverse=True)

    return tidal_range_list[-3:]


def format_tide_data(daily_tide_list, spacing=3, emoji=chr(0x1000A4)):
    """
    Transform list of DailyTide class object to formatted tide data string.
    """
    space = " " * spacing
    formatted_tide_data = ""
    sorted_tidal_range_list = _get_sorted_tidal_range(daily_tide_list) # Include three sorted elements in list.
    for daily_tide in daily_tide_list:
        formatted_tide_data += (daily_tide.date + space)
        formatted_tide_data += (daily_tide.date_lunar_calendar + space)
        formatted_tide_data += (daily_tide.tidal_range + space + "\n")

        for tide in daily_tide.tide_info_list:
            formatted_tide_data += (tide["tide"] + space)
            formatted_tide_data += (tide["time"] + space)
            # Add fire emoticon if tidal rande is less than -100.
            # level = abs(int(tide["tidal_range"])+100)//15 if int(tide["tidal_range"]) + 100 < 0 else 0
            # Add fire emoticon if to lowest three tidal range.
            level = sorted_tidal_range_list.index(int(tide["tidal_range"])) + 1 if int(tide["tidal_range"]) in sorted_tidal_range_list else 0
            formatted_tide_data += ("高度: " + tide["tidal_range"] + emoji*level + "\n")

    return formatted_tide_data


def get_several_days_tide_data(daily_tide_list, days=7):
    tide_data_list = []
    for idx, tide in enumerate(daily_tide_list):
        if idx < days:
            tide_data_list.append(tide)
            continue
        break

    return tide_data_list


def get_latest_tide_data(daily_tide_list):
    tide_data = None
    for tide in daily_tide_list:
        tide_data = tide

    return tide_data
