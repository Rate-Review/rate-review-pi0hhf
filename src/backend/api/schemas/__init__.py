"""
Initialization file for the API schemas package that centralizes and exposes all schema models for validation and serialization across the Justice Bid Rate Negotiation System.
"""

from .users import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDB,
    UserOut,
    UserList,
    LoginRequest,
    Token,
    TokenPayload,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    MFASetupRequest,
    MFASetupResponse,
    MFAVerifyRequest,
    UserSearchParams
)
from .organizations import (
    OrganizationBase,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationInDB,
    OrganizationOut,
    OrganizationList,
    OrganizationSearchParams,
    OfficeBase,
    OfficeCreate,
    OfficeOut,
    DepartmentBase,
    DepartmentCreate,
    DepartmentOut,
    RateRulesUpdate as RateRulesSchema,
)
from .peer_groups import (
    PeerGroupBase,
    PeerGroupCreate,
    PeerGroupUpdate,
    PeerGroupOut,
    PeerGroupMemberAdd,
    PeerGroupMemberRemove,
)
from .attorneys import (
    AttorneyBase,
    AttorneyCreate,
    AttorneyUpdate,
    AttorneyInDB,
    AttorneyOut,
    AttorneyList,
)
from .staff_classes import (
    StaffClassBase,
    StaffClassCreate,
    StaffClassUpdate,
    StaffClassInDB,
    StaffClassOut,
    StaffClassList,
)
from .rates import (
    RateBase,
    RateCreate,
    RateUpdate,
    RateInDB,
    RateOut,
    RateList,
    RateHistoryEntry as RateHistory,
    RateType,
    RateStatus,
)
from .billing import (
    BillingBase,
    BillingCreate,
    BillingUpdate,
    BillingInDB,
    BillingResponse as BillingOut,
    PaginatedBillingResponse as BillingList,
    BillingStatistics,
    MatterBillingResponse,
    BillingImport,
    BillingImportResponse,
    BillingExport,
    RateImpactRequest,
    RateImpactResponse,
    BillingTrendRequest,
    BillingTrendPoint,
    AFAUtilizationResponse
)
from .messages import (
    MessageBase,
    MessageCreate,
    MessageResponse as MessageOut,
    MessageUpdate,
    MessageThreadCreate,
    MessageThreadResponse as MessageThreadOut,
    MessageList,
    MessageThreadList,
    MessageFilterParams
)
from .negotiations import (
    NegotiationBase,
    NegotiationCreate,
    NegotiationUpdate,
    NegotiationInDB,
    NegotiationResponse as NegotiationOut,
    NegotiationListRequest as NegotiationList,
    NegotiationStatusUpdate,
    ApprovalStatusUpdate,
    NegotiationAddRates,
    CounterProposalCreate,
    NegotiationRateActionRequest,
    NegotiationFilter,
    NegotiationAnalytics,
    NegotiationDeadlineUpdate,
    NegotiationFinalize
)
from .ocg import (
    OCGBase,
    OCGCreate,
    OCGUpdate,
    OCGInDB,
    OCGResponse as OCGOut,
    OCGListResponse as OCGList,
    OCGSectionBase,
    OCGSectionOut,
    OCGAlternativeBase,
    OCGAlternativeOut,
    OCGFirmPointBudget,
    OCGStatusUpdate
)
from .analytics import (
    AnalyticsRequest,
    AnalyticsResponse,
    RateImpactRequest,
    RateImpactResponse,
    PeerComparisonRequest,
    PeerComparisonResponse,
    HistoricalTrendRequest,
    HistoricalTrendResponse,
    CustomReportDefinition,
    CustomReportRequest,
    CustomReportResponse,
    SavedReportListRequest,
    SavedReportListResponse,
    TimeSeriesPoint,
    TimeSeriesSeries,
    Visualization,
    TopAttorneysRequest,
    TopAttorneysResponse
)