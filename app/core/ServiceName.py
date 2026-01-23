from enum import StrEnum


class ServiceName(StrEnum):
    """
    Enumeration of available service names in the application.
    
    Defines the unique identifiers for different services that can be accessed,
    including time series analysis, preprocessing, donation, computer vision,
    and advertisement services.
    """
    TimeSeries = "service_TimeSeries"
    PreprocessingTable = "service_PreprocesingTable"
    ComputerVision = "service_ComputerVision"
    Advertisement = "service_Advertisement"
    Science = "service_Science"
    Blog = "service_Blog"
    Donate = "service_Donate"
    Chat = "service_Chat"
    Default = "service_SersivesRegistry"
    ServicesRegistry = "service_SersivesRegistry"
    TestStend = "service_TestStend"


