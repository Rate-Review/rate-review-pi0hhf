
1. [Law Firm Background](https://docs.google.com/document/d/1xEtOyrG_HgMwuE3WMz-F3oyusJQpis24/edit#heading=h.8d5yqvgmn1dl)

2. [Client Background](https://docs.google.com/document/d/1xEtOyrG_HgMwuE3WMz-F3oyusJQpis24/edit#heading=h.4og0y4ph9qch)

3. [System Considerations](https://docs.google.com/document/d/1xEtOyrG_HgMwuE3WMz-F3oyusJQpis24/edit#heading=h.fsyk4dk4x5so)

4. [Design Instructions](https://docs.google.com/document/d/1xEtOyrG_HgMwuE3WMz-F3oyusJQpis24/edit#heading=h.30j0zll)

5. [AI-First](https://docs.google.com/document/d/1xEtOyrG_HgMwuE3WMz-F3oyusJQpis24/edit#heading=h.xuej7ew95jho)

6. [Functionality](https://docs.google.com/document/d/1xEtOyrG_HgMwuE3WMz-F3oyusJQpis24/edit#heading=h.1fob9te)

****

## Problem & Objective:

**Problem**: Every year, law firms want to raise rates and it is a sloppy process because Clients’ ebilling systems do not accommodate negotiations. eBilling systems can either accept or reject rates submitted by law firms. The initial request to submit rates is sent by email, and all back and forth negotiations takes place via email. Further, all analytics for newly proposed rates is performed outside of the system. 

**Objective**: Systemize the new rate negotiation process, from initial request to loading approved rates in the client system, while providing actionable recommendations, based on analytics, including 3rd party data, and embedded ai design. 

## General considerations and background for law firms:

 Law firms generally have more accurate billing and rate  history than their client. They also have more detailed information such as the time attorneys spent working via a billable hour, time the attorney spent working on a specific project or under an alternative fee arrangement (AFA) where the hours are not presented to the client but the client wants to know the balance of hours for attorneys that worked on an hourly basis vs. on a project/AFA. Also, each attorney has a standard rate. It may be based on their staff class (years of experience as associate, partner, etc), or it is unique to the individual attorney. Law firms maintain different rates based on the attorney’s office location and practice area, which is also often reflected in the staff class rate structure. Staff class rate structures vary by client (i.e., one client says a Jr. Partner has two or less years of experience, another client may say Jr. Partner has three or less years of experience). One attorney may have multiple billable rates based on the office they are billing from. 

Law firms vary in size and sophistication. Clients, as part of the annual rate review process, will want the law firm to provide historical billing, utilization, hours, and other information from the law firm for the work done at that client. Some firms would prefer to integrate in order to provide this data to Justice Bid directly, others would prefer to upload via an Excel template, and some are so small it is easier to manually enter information on screen via a form. Each would require their own interface and, in the case of any API connection/integration, configuration of the API and field mapping. The API may will be used at the end of negotiation to send rates back to the law firm’s system. Additionally, the law firm may choose to export rates via excel so they may manually upload into their system. 

Two constants for attorneys are they will all have one “Current Standard Bill Rate” (also known as “Rack Rate”) and one Timekeeper ID (which is  a unique identifier for a specific attorney at a specific law firm). Attorneys have Bar ID’s by State, which may be used as an identifier. 

The law firm will want the ability to see billing and rate history, supported by analytics, when proposing and negotiating rates to a client. 

Law Firms may provide Attorney profiles. They will need the ability to configure these manually but also may be provided via API from the law firm to Justice Bid. This requires a an API setup and configuration, including field mapping. Attorney profiles would include identifiable information, such as phone and email, bar IDs, court admissions, bio, experience and awards.  

## **General considerations and background for Clients:** 

Each client will have different pricing with each law firm. This includes pricing by named attorney, which may have different billing rates depending on the office the attorney bills out of. So, one attorney may have three different hourly rates, each unique to a billing office with its own currency. Pricing by staff class which may vary by office and practice area. Clients may ask the firm to have staff class rates only for a select few practice areas and locations, and lump all of the rest of the practice areas as “all other”. Staff class rates may also be structured as a defined discount percentage across all standard staff class rates regardless of practice or geography. It may be the same discount or a specific discount per staff class or geography. This is to say, there are many different variations of pricing that clients prefer for their business need .

Clients will set different “rate freeze” periods. This is a time when the client allows new bill rates to take effect. This is often two years, but sometimes one year. The client want the ability to define a limit on the rate increase from year one to year two. For example, the client can say that in year two rate increase will be limited to 3%. The law firm must agree to such time period.

Clients will want to connect their ELM or eBilling system to Justice Bid for the purpose of sending Justice Bid historical billing information and, after the rate negotiation, sending the negotiated rates back to their eBilling/ELM system. For this they will need the ability to configure the API, map fields, and test. 

General considerations and background for Justice Bid managing the application: The application would not allow for self-registration. Invitations to Justice Bid would be initiated by a client to a law firm, or by justice bid to a client or law firm. Or the law firm or client can invite members of their own organization. 

Justice Bid must have the ability to act on behalf of any user of a client or firm. 

## **System wide considerations:** 

For the purposes of this application let’s call any client or law firm an organization. Clients, Law firms and Justice Bid (where Justice Bid is the system administrator). We’ll need the ability to have multiple levels of account management where an organization admin can set up users and define permissions, including workflows end users who would have approval rights along a workflow. There must also be self-service sso configuration for each organization, including Justice Bid. 

All changes must be tracked in a log file, timestamped and who took the action. This log is available to Justice Bid across all, and to the highest permission user(s) within an organization for only those logs related to that organization. 

There is a third party data service called UniCourt, that has an API with attorney data. This has attorney mapping of attorney name and law firm, and can also match by bar ID. The data available is performance oriented and will be helpful for a client considering a proposed rate. The architecture should consider utilizing the API and storing such attorney data, as well as fetching refreshed data regularly. This data may then be made available, by Justice Bid configuring such available data by Org, if the Org has such permission. 

Ai may be used to assist in analytics by both law firms and organizations using Justice Bid, as well as justice bid itself. The architecture must account for permission based access to the organization’s data. For example, a law firm may request Ai to analyze their rate history across one or more clients. Similarly, a client may ask Ai to analyze rates at one firm or across a selection or all firms for a defined time period. But they may not ask Ai about data that is not theirs. For example Client A cannot ask about rate information from Client B or Client C. Similarly, Law firm A cannot ask about rate information from Law firm B or Law firm c. 

There must be a notification system to alert organizations and users of any notifications. There must be different levels, including urgent. 

There must be a chat system between two organizations, where messages are logged. This is to facilitate negotiations. Messages are identified as notifications. The architecture must consider the chat system and notification system. 

## Design Instructions:

- The interface should be intuitive, modern and professional. Favoring responsive icons in instead of buttons where appropriate.

- Do not show decimals when showing currencies. We are dealing with larger dollar values and pennies don’t matter.

- Never show more than 2 decimals for any percentage

- Use breadcrumbs for easy navigation back

- Front end code to be in React.js

## 

## Ai-First: 

This application should be "ai first", meaning generative ai is utilized throughout the application. Users should have the ability to chat with any data available to them based on their permissions. For example, a law firm admin can only ask about data related their firm. User-based-permissions must also be incorporated. For example, a pricing administrator can view all rates within their organization. An approver of a defined "Group" or specific client or specific law firm, can only chat with data permissioned to them.

1. Ai-First objectives

   1. Architect such that the customer can allow their own AI environment to run all ai functions. This is for data privacy/security. If the client wants to use JB’s Ai environment, they can. Or they can opt to use their own. Ideally, they would say what LLM they are using and we could recommend which version for each of the different AI functionalities we have available (i.e., client says they use OpenAi, we would prepopulate a configuration suggesting: o3-high for summary, 4o for pricing, etc.). 

   2. Process Management: Review all activity between a client and law firm and help them focus on what is most important.

   3. Suggest follow-up messages to send. 

   4. Automatically identify and recommend attorneys based on UniCourt data, RFP submission data (from legacy Justice bid), current approved rates, and ratings. Give a brief explanation of why you suggest each attorney, in priority order. Allow the user to ask for comparison across the recommended attorneys. 

   5. “Recommended Actions”. Envisioning an actionable “to do” list where ai has gone through and calculated everything a user needs to do, in priority order. Each recommended action can be executed on screen. Each recommendation has supporting information such as why it is important. An example recommendation: Send counter-proposal to \[law firm\]. The user can open up this task, see a message already drafted. The user can see an “internal only reasoning” that says why this action. why this message. why these counter-proposed rates. The user may edit right there, and send. Then move on to the next recommendation action… 

The objective being, every available action a user can take should be prioritized for them. If the users skips an action and jumps to another, system takes notice and stores it. Over time, it helps prioritize better. 

6. An A genetic workflow system suggests approval flows. When something is sent for approval to a user the application includes a summary of the approval request, including background. The approver may ask follow up questions to learn more about the specific approval request such as comparative analytics or further background on the source or history. The workflow agent will consider context risk urgency Present options, when appropriate, and considerations for those options. The Workflow agent will consider past decisions of each individual user, including an approver, to make more accurate suggestions for what they may do next. Overtime, the application must learn the behavior of the user to proactively make available answers to potential follow up questions the approver may ask.

7. Enable a user to have conversations with the application, using all Evaluate data permissioned to the user. 

8. Automatically Review any new rates that are requested or submitted and recommend a course of action after considering: compliance against the request timing rules (i.e., 90 days notice; one request per 12 months), Rate Rules (i.e. ,max 5%); compare current and proposed rates to their peer group rates, evaluate attorney performance based on a combination of unicourt data and The attorneys ratings of individual attorneys, the utilization of AFA’s by the law firm and attorney (i.e., more AFA means hourly rate less important).  Example outputs of this would be:


1. Recommendation to approve a request and why

2. Recommendation to reject a request and why

3. Recommendation to counter propose one or multiple proposed rates, what the counter-proposed values should be, and message to be sent back to the law firm. 


 9. Automatically recommend Peer Groups, for both clients and law firms, based on whatever billing history is available. 

10. Client may establish one or more email addresses they can provide to law firms, such that the law firm can submit a question, message or request, the application will review and route to the appropriate internal workflow. For example, a law firm emails to ask to add a new attorney to the account. This would be transformed into a “New Attorney Request”, the client could approve the request, and the firm could then send the rate. If the firm included relevant details in the email, the application would populate what was available, but still allow the client to review and approve/reject.  

11. Support Personalization at the user level. As envisioned with the highlighting of text in Proposals, where the thumbs up/down “train” ai to know what to look for at an individual user level. Next time the user has a proposal to review, it would be pre-highlighted showing what the user likely thinks is good/bad/idea. Example below. But this concept of personalization is not limited to proposals. it would mimic the style of messages the user drafts. Approach to negotiations. It learns what the user does so it can do more of the task for them, the way they want it done. 

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXentKKWwSbqQiwr7QQpXT2lqg7-O9zO4RLDb7UGkTnttky7zWwHXoDb4gvQvvyevt5tSgNdtKjZ-IUp3uMxOIlPFWcg8Fy3Awj20fa5AaPJ6djLJZ6ULD_QhTkNeafSC7FVdxVcqurzSTCKavfupPY?key=kFe-0bm0qP_I7_1RteZOAKmA)

Phase 2: Ai Counsel Selection

Bid Agent automates the bid process. 

1. A new matter is discovered by the system, either uploaded by a client or received from 3rd party provider (i.e., UniCourt). 

2. The matter is reviewed  to determine risk, legal cost benchmark (using all client billing history to provide an anonymized cost range).

   1. Benchmark cost to consider the historical spend each client had with a firm at a given time for a comparable matter; the industry of comparable matter; the prestige of the client logo (i.e., well known or lesser known); the prestige of the matter outcome (was it a big M&A deal? Big public litigation? Supreme court?)

3. Ai suggests how to proceed, to contact a firm or take out for bid. 

   1.  

4. The contents of the matter detail generates the RFP (summary, questions, pricing)

5. Firms are automatically suggested, based on if they are on panel, what list they are on (Lists from Legacy JB – i.e., Panel, Tier, Geography). 

   1. Client Side of Bid process: Ai reviews responses, suggests follow-up questions based on each answer, specific to each firm or to all. \[Critical here, cannot use content provide by another firm with this follow up question\]. The firm responds to follow up questions. Ai reviews responses to evaluate completeness of understanding. Ai reviews proposed attorneys and compares to recommended attorneys (per the flow defined by: Automatically identify and recommend attorneys), and compares anticipated cost to proposed cost / estimated fees if hourly (cost budget based on billing history for similar matters). 

   2. Firm Side of Bid Process:  Automatically recommend responses based on previous responses from the firm. Give feedback on strength of proposed team. None of this can be in relation to any attorneys or answers from any other firm. They can only get feedback with respect to their firm and history. For example, if they bid $X on a matter, and won, and now they propose a much higher price of $Y, this should be identified to the firm. 

****

## 

## Specific functions to include: 

1. While in development, the root landing page should provide an inter for the application Administrator to view a list of all law firms and clients, from the mock dataset you will create, and login as any of them, and act on their behalf. Do not require authentication at this time. User level security will be added in the future. 

2. For both clients and law firms, create an intuitive dashboard that serves as the hub for all actions they will need to perform. There should be a component for their notifications and messages, actions required based on dates approaching. It should be well organized and intuitive. 

Example:

![A screenshot of a computer

AI-generated content may be incorrect.](https://lh7-rt.googleusercontent.com/docsz/AD_4nXfNfMw12Z650ACPHA_4OlndoNAqpymdVQW0b7lbrUm4QGNHOU7xf86bngEgmLwo8dHIRewaOoAFcMp9g-CYLOiyf2FN84rCTu6PFFR8fov7eaWieU0zYkMtNtQxdQK6Ua3Rq9nUj8GW3NMR-sja8Jw?key=kFe-0bm0qP_I7_1RteZOAKmA)

3. A critical element available throughout the application, persistently available in the top nav bar, will be an AI Chat interface to ask questions about any aspect of their interactions with any law firm (for clients) or clients (for law firms).  The AI chat should be connected functionally to the application’s backend such that you can take actions within the application via chat. More on Ai integration below.

4. Client to have an interface in which to define Rate Rules. This includes Rate Freeze, Rate Request Window (start and end date), Rate Request Notice (i.e., 90 days), Rate Request Frequency limit (number of requests in defined timeframe). 

![A screenshot of a computer

AI-generated content may be incorrect.](https://lh7-rt.googleusercontent.com/docsz/AD_4nXfgMHwpArfQmPKi9VD8ojeBiqpui2GNiaLxf3BXSV9WsuKmgbfYARGKbTHWV2-ZUIlav-QqDXpiAVdKXl4OHBBCy0qVq_53JVVpWYw6LMfdPWnAY_PVUHGdtCVHDqMxs8bYpoTz5vHQEnCaV_GR43E?key=kFe-0bm0qP_I7_1RteZOAKmA)

 5. Ability for law firm to view a list of all of their clients. They may click on a client and request permission from the client to submit new rates. The request would include the ability to add a formatted message. This request will be received by the client as a notification on the client's interface along with the associated message that would start the parent messaging thread for the request and subsequent Rate Negotiation (if new rate submission request is allowed). 

 6. Clients may also initiate a new rate submission request by selecting or adding a law firm, and sending a request to the law firm. This would act like an “approved request” to the law firm and follow the same flow as if the firm made a request to the client and the client approved such a request. The client would have the ability to add a formatted message to this request. 

 7. Client may request a New law firm to submit rates. The new firm can come from an existing firm setup within the application by any other client. The new firm can also be created via email invitation. A new Firm would bypass the time-oriented Rate Rules since they are new. 

 8. A client  may request a specific law firm add a new named attorney, which is not subject to the rate rule timing. However, the attorney would be submitted like a newly proposed rate, following the rate negotiation process. 

 9. A firm may submit a New Attorney request. This, like the ability for the client to request a new attorney, would not be subject to the rate rule timing. If allowed by the client, it would follow the same rate negotiation process. 

10. Firms and clients are organizations grouped together by their business email domain. 

11. Create an interface for the client to receive new rate submission requests. It should clearly identify the firm making the request and enable, via an elegant responsive icon, display the request message in a pop-up. There, the client may "allow" or "reject" the firm's request, write a message in response and set a deadline for rate submission (the time by which the law firm must propose new rates for all named attorneys and staff classes). 

12. Also in the client's rate request interface, the client should have needed information about the rate, billing and performance history of the firm and named attorneys. The client should also view the firm’s rate request history I accordance to the rate rules defined by the client. The reference for Rate Rules are to be presented based on the result of the rules, not just showing the rules. For example, show the number of days remaining for the current rates, if there is an expiration. If no expiration, show “rates ongoing”. If rates have an end date, show number of days until rate freeze expires. If client has a notice period, show the request relative to the notice period (i.e., 90 days notice period) such that new rates won’t be effective until notice period is satisfied. Other rate settings included max number of requests in a given time period (i.e. every 12 months). Defined request period (start and end date; Q3 of each year). Indicate with visual positive confirmation that the firm is in compliance with their signed Outside Counsel Guidelines (which contain specific Rate Rules they have agreed to). 

13. Create a backend data structure to support: 

    1. variations in historical data that will be provided by clients. This includes accepting data that ranges from granular invoice level data to summary annual billing data by staff class. This data may be provided by clients or law firms, and should be treated separately. This means you will not only have hourly billable and expense data, but hours associated with AFAs (which are essentially projects)

    2. Current and historical standard, proposed, counter-proposed, and approved Rates by named attorney and staff class, where staff class can be defined by the client in their settings. 

    3. One attorney can have many staff classes as each client may assign their own staff class in addition to the default staff class as defined by the Rate Negotiation application. 

14. Create a flexible interface for the client to Configure an API to their ebilling system (such as Onit, Team Connect, Legal Tracker or Bright Flag) in order to receive their billing history. The flexible API configuration interface should include drag and drop field mapping from the fields received via API to the underlying data structure of this Rate Negotiation application. The configuration should be separated into configuring for “Importing” data, and “Exporting” data. Importing would apply to historical rate and billing data. Exporting would be for sending rates that were Approved within the Rate Negotiation application back to the ebilling system, where the new approved rates would be sent back to the client’s ebilling system. Both importing and exporting should allow the client to Preview the data. Both importing and exporting should allow the client to filter based on available data factors, for example, by law firm. The interface should also allow the user to decide if they wish to append data when sending, or overwrite. The data structure should support logging in case the user makes a mistake and wishes to revert back to a previous time.  

    1. Here is one example, showing after an Excel file was uploaded, the column headers were identified, and allowing them to be dragged and dropped from the Excel Columns to the Application Field (although this example is bad because it shows an Attorney Name mapped to Firm Name, but gives you an idea of how it works even if a user makes a mistake)

![A screenshot of a computer

AI-generated content may be incorrect.](https://lh7-rt.googleusercontent.com/docsz/AD_4nXchpYi4fsem-hEg1ZKuhziVy5Ncbmcyt3f-EJCpQGWTuR_iCtQKz5pCBthoTCHEGuby72c_U4LOcbXAQtZhLaqLJwLkJBY8JRYsSpbLV2-u5iyQMJ_mwlJLk6WNb38ahk-9Dta9R14caAgE5WHfgQ0?key=kFe-0bm0qP_I7_1RteZOAKmA)

15. Configure flexible file upload and export with similar configuration as the API. Further explained at a later step. 

16. 

17. Create an interface for Client Settings, where the client can configure aspects of how they govern their outside counsel

    1. Add AFA Target function to allow a client the ability to configure a target % of total fees by firm that should be based on Alternative Fee Arrangements, the remainder should be hourly, for a time period the client defines. This information will let the client quickly see if the firm has historically met the goal, for example, to have 70% of fees be based on Alternative Fee Arrangements as they are preferred to allowing uncapped hourly billing.

    2. The client my use the application’s pre-defined staff classes, or they may define their own. To define their own staff class, the client must pick how they segment outside counsel attorneys. Either by, graduation year, bar year, years in role. The client must select one that will be used for all of the staff classes they configure. The method of defining a staff class will be appropriate to the selection. If bar or graduation year, it will be X years since graduation/bar. If years in role, it will be a selection of X years to X years. Where years cannot overlap. 

![A screenshot of a computer

AI-generated content may be incorrect.](https://lh7-rt.googleusercontent.com/docsz/AD_4nXchgGSL4iuF5z0X85Lrkdreb9XTrN4gJ-alWStX3vPTj7QhQXPXmFEWswW9GpYbGpQAilrooh7wgDOPurTtzaQflMyRvgZTkMcfwJgwk6KbHJ3lsRZarsllTWy1kuSO-3GjD4yi6ZPnNuAWyG5nQLY?key=kFe-0bm0qP_I7_1RteZOAKmA)

3. The client may establish rate rules by staff class, such as a max increase %. The client may set individual max increases or apply one max to all. The client may choose to display this value to the law firm or not. The client may decide what happens if the max rate increase is exceeded, including auto-reject, allow but turn red so the client and law firm knows they are in violation. 

![A screenshot of a computer

AI-generated content may be incorrect.](https://lh7-rt.googleusercontent.com/docsz/AD_4nXemMxhOS6G81TkCk1HcR0PdsiPMIHrkWBAmOv-PtZS54tlzZytLKhcWJISwN5RayC0ZHMDLobm1I6sVNZJs2lugktM7TLYaESCCTP4NDtnwL--l0X-IFVQy-eiNF3SyX6YruGaavcsEK1G5WDtpD9A?key=kFe-0bm0qP_I7_1RteZOAKmA)

 4. The client may request justification for any rate increase, or selectively based on the rule. For example, only require an explanation if the increase is greater than X%, greater than the defined rule, greater than a certain fixed dollar value

 5. The client may click a toggle to require one rate per attorney

 6. The client may set a default rate-freeze period, which has an Effective Date and, if set, an expiration date

 7. The client may negotiate a defined rate timeline, where year one is negotiated and year two has an agreed percentage rate increase.

 8. Client may define the rate notice period, which is the number of days the firm must give before requesting such rates become effective (i.e. ,90 days)

 9. The client may define a “New Rate Submission Window” which has a start and end date that repeats each year. During this time, firms are allowed to submit new rate requests. 

10. The client may define a maximum number of rate requests during a set period of time. Interface to include X requests in X (selector of months or years).

11. Defining Peer Groups is a critical component as Peer Groups will allow comparison of factors, such as current or proposed rates, across peer group members, their average or standard deviations. Clients must be able to define law firm peer groups. The interface must allow the client to select a client in whole, or a portion of the client by office geography and or practice area. One part or a law firm entirely may be part of many different peer groups. The purpose of the peer groups is to compare rates across the defined peer group. 

12. The client may configure to view all rates in one currency or they may view in the original currency.  Use the latest average currency conversion. Allow the client to override the suggested currency conversion rate. 


18. In Client settings, create an interface for client to create Outside Counsel Guidelines

    1. Outside Counsel Guidelines (commonly referred to as OCG's). Here, the client to defines their outside counsel guidelines that the firms will sign to agree. The Rate Negotiation Application will start with a default OCGs the client will further edit. Included as default sections in the OCGs will be any Rate Rules as established by the client in Client Settings (i.e., rate freeze period, rate notice period, 

    2. Requires the ability for the client to build what is essentially a document with sections and subsections. Allow the client to identify any section or subsection with a toggle called "Negotiable". If the section is marked "Negotiable", the client may add one or more alternative versions of the same section. The alternative version must have a title. The client must also assign a numerical point value to the alternative section. The reason for the points is that the Client will later have the ability to give each law firm a number of points to negotiate in the Outside Counsel Guidelines. The law firm will then be able to spend those points by choosing any combination of the available alternative section language, thereby spending their "negotiation points" according to the value the client has assign. It will then be up to the law firm to find the combination of negotiable sections with alternative language that fits within the points given to them by the client.

    3. Part of Outside Counsel Guidelines will be settings that are configured by the client in Client Settings. This includes Rate Rules, Rate timing, and other settings configured by the client at the time the law firm is reviewing such Outside Counsel Guidelines. Once the law firm signs the OCGs, any further changes to Client Settings will not impact what the law firm has agreed to. At the end, when agreement is reached, there should be an electronic signature functionality with name, title and date of signature.

    4. Conversely, the law firm will have to have such functionality on their side to view outside counsel guidelines with each client who has such functionality enabled. 

    5. Examples of how outside counsel guidelines work:

![A screenshot of a computer

AI-generated content may be incorrect.](https://lh7-rt.googleusercontent.com/docsz/AD_4nXcKN8P146kNCj0YRKG4njBJWuwe0KTrs_AAT6Webl73danfulRBO_CorFAb-h2ZzRIAZ-p9l8fTwun8IV0wwrjUVMFbNUhkglrJtS8FwwAVLCiO66l6u_u0LmtTm8h8vota_sX-tCZEhbVImseQSqE?key=kFe-0bm0qP_I7_1RteZOAKmA)

This example Shown here in Preview Mode, where this Firm spent 3pts on the first clause and it is visibly deducted from their 10 points - leave 7 to spend

![A screenshot of a computer

AI-generated content may be incorrect.](https://lh7-rt.googleusercontent.com/docsz/AD_4nXcbBTpuSAvBCtFEvy2zmhLyAVmWypABNIbGgLx1bH-6z9nLwHmLBgM9Jf0VR_Nj9MlDZjArpuQkwp8BTghQII3ufLoyAEPRcR6LZCm4Xk3IuyzAw4joaKVWAlABicLr6UhuyIO7-ZLVo8AFB4bJTf4?key=kFe-0bm0qP_I7_1RteZOAKmA)

19. Peer Groups are critical for law firms as well. This allows a law firm to define peer groups of clients. Law Firms will use peer groups of clients to guide their rate proposals based on how important the client is, how much the client spends with the firm, the client locations and practice areas, and AFA utilization. For these reasons, Law firms require an interface to create peer groups of clients. Any current and proposed rates, billing history loaded by the law firm, and other views must all have the ability to be associated with a Client Peer Group.  

    1. Example 1: Creating a peer group

![A screenshot of a computer

AI-generated content may be incorrect.](https://lh7-rt.googleusercontent.com/docsz/AD_4nXem00IBbMA2bzTkawL92-xl2gWkOzz70yG1rNDrbZUanC-D7KqEeuzxsQBQI_NCwWVVloKziWX7SeiYYcu84h43bmNBp26iK6wbMq8KCoFO8D2EuNqUvI62K-r1Wpk5PFlPaxcJV1neSvQ7ksHTTeY?key=kFe-0bm0qP_I7_1RteZOAKmA)

![A screenshot of a computer

AI-generated content may be incorrect.](https://lh7-rt.googleusercontent.com/docsz/AD_4nXcFudKtS2VUKzLvqHMU1J1Kp94mwXxX5UNQ2a-60M-t-bgDJsNtStGDNqjl3iF8EcEv9bMAS5hpL8b6jD01zRGX1vzYtm3OH8vO4N4KKXXWxfZzy1Mek6dR36l5CSeBSNMumFYbGlMo7JmNi482m1M?key=kFe-0bm0qP_I7_1RteZOAKmA)

20. Create an approval Workflow for negotiating rates, for both within a client and withing a law firm. 

    1. For client, allow the client to define approvers of specific law firm rates. The client should use the same “Law Firm Peer Group” functionality setting but this time to define Departmental Approval Groups. Each Approval Group requires an approver to be setup with a name and email address. The Departmental Approval Group will have a more consolidated interface where they can see the overall Impact summary analysis of the rates proposed by firms in their peer group. From there they may drill down further, all the way to the individual timekeeper proposed rate. 

    2. Law firms use the same type of Client Peer Group to create Approval Groups for their part of the rate negotiation process. This way their internal department or office leaders can approve the new rate submission. Just like the client can, each Firm Leader Approval Group approver will be presented with high level summary analytics, which they can drill down to the proposed rate of a named attorney to a specific client. 

    3. The Approver, be it on the client or law firm side, may have “suggested” proposed rates or counter-proposed rates, and easily see what the impact is of this change using the previous years hours.  

21. The law firm will only see the staff classes, named attorneys, practices and geographies where the client allowed new proposed rates to be submitted. The staff classes will be represented based on the Client’s definition of staff class. Each attorney will have a bar date (the date on which they passed the bar), graduation date (the date on which they graduated from law school), a promotion date (the date on which they were promoted to their current role). Using a combination of these data, each law firm attorney will be appropriately placed within the clients’ staff class framework. 

22. If the law firm wishes to submit rates for a staff class, named attorney, practice or office where they do not have any historical billing (i.e., net new addition), the law firm must have an interface to add such request as a "new billing entity rate setup request" in their interface. This request will be presented to the client along with the rest of the law firm's request. If rates are approved for the firm, this would be treated as a new rate submission request and follow the same procedures as existing rate submission request. 

23. Ability for Client to intake historical rates by attorney for each of their law firms. 


1. Option one, allow the client to configure an API feed from their ebillling system (Onit, Team Connect, Legal Tracker, BrightFlag) to send historical rates by firm by timekeeper. The client will configure this by selecting their ebillling system. Next, the client will enter the API endpoints. Next, the client will be presented with required fields in this rate negotiation application in a list in column 1, and next to each application field, present the field received from the ebilling system. The client fill use the drop down to map the fields from their ebilling system to the rate negotiation application. Allow the client to "save" API configuration. 

2. Option two, provide an Excel template for the client to populate with historical rates by firm by timekeeper (i.e., attorney). The client then uploads the historical rate table for one or more firms.

3. Must have interface for client to positively match each law firm identified in the uploaded rate table to the existing database of law firms. The law firm name and email address of the contact provided in column two (of the template), will assist in matching to any existing law firm organizations based on a match of the law firm contact's email domain. 


24. 24. Law firms must be easily able to track their clients separately firms will be simultaneously negotiating rates with many clients, in addition to adding new. 

25. The law firm may, similar to the client, choose to interact with the application via API, which they configure, or Excel template upload. Law firm to configure an API to their attorney rate system of record. They will need to configure or map each of the required fields to the appropriate fields in their system using the same type of API configurator as available to the client, where first select system, enter API endpoints, and finally map the fields.


1. Law firm to download their file or blank, add attorneys by name and TKID, add current rate (optional), enter new proposed


26. Create an interface for Rate Negotiations to take place

    1. Client and Firm interface to provide 


1. An ability approve, reject, propose, and counter-propose a rate

2. An ability for the law firm to enter a rate, or approve a client’s proposed rate

3. An ability to multi-select bulk actions:


1. Approve

2. Propose a rate (apply X% discount to Rack Rate)


2. Filter based on staff class, geography  


2. Here is an example, although it is missing the Peer Group for reference:

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXeYgClhWHrXvskZBmKIwDZWtdcQ3BwD1Av-cUEmb_WpkHlYDONRBl962R1f-E3bHnNqQ-F1JFx_d67wYT_4XTbc373Qr3o3sTqBGVoZK4Xa0pBgY0CcHeaqYqfb8zqBjY7iDWFvbOz1RAbkZHIDizI?key=kFe-0bm0qP_I7_1RteZOAKmA)

3. When counter-proposing a rate, by either the client or law firm, show a history of the rate and date proposed. Previous proposed rate should be presented with a line through it, only showing the latest available rate proposed for approval. In addition to the rate and date, include the ability both the client and firm to view any message sent along with the proposed or counter-proposed rate. The ongoing negotiations of rates is on the left side of a pop-up, while the associated message back and forth are on the right. At the bottom of the rate negotiation pop-up is an approve button. 

![A screenshot of a computer

AI-generated content may be incorrect.](https://lh7-rt.googleusercontent.com/docsz/AD_4nXes_bYZYbz7urX6PD9eJjIa9qVgtm8H0cmk_ZN_o7dO8L9VHyOUhBLVa6ZklUOuElmRVZ6DUDWtDRCAh1uY7xQj2QJqKWLhKZn62rRglMhkZofXo_4DJ3eVq62ubOn6KgxhprH_Jq5MQvlyQNr08Kk?key=kFe-0bm0qP_I7_1RteZOAKmA)

4. All rate changes are timestamped to provide ongoing analytics.

5. The rate negotiation must have a “Real Time” toggle, which by default is set to off. When it is off, there is a button called “Send to Firm”. This means that all of your rate approvals, rejections and counter proposals are saved and sent at once. When the toggle is sent to “Real Time”, whatever action the user takes is immediately communicated to the counter party (i.e., if client approves a rate, it immediately appears as approved on the Law Firm’s view as that rate being approved).  


27. Create a Messaging interface that is hieratical, such that a parent message is related to the overall rate negotiation between a law firm and a client, starting from the initial request for new rates. Messaging should be a separate standalone tab with filtering. This way the message history is organized. 

    1. The 2nd level down in the message hierarchy will be one or a series of chats related to one or more staff class and or named attorney negotiations. If bulk action is used to respond, and a message is added, this would be a new message thread at the messaging level 2. 

    2. Within messaging, allow filtering and search.  

    3. When rates are submitted by a firm, or counter-proposed by the client to the firm, they may include a message of up to 2,000 characters. Messages should have formatting options, such as bullets, numbering, bold and italics. 

28. Analytics: Both the client and law firm must have an interface showing rate analysis on historical vs. proposed rates; with drill-down abilities to review discount trends, rate increase trends, starting rate vs. approved rate, at an individual firm, selection, group (lists) or all firms. 

    1. Example Rate Impact. 

![A screenshot of a computer

AI-generated content may be incorrect.](https://lh7-rt.googleusercontent.com/docsz/AD_4nXem9cQmIYuZzIyDcwgDLOUornT920lG-XVsbz_T_1jt74cDWfLNCcFzXlUSjF3h76DIkWznQBeDrbanwI1ZIb_J4REbUVD77Lsp0VpdeKqNWpRZH1Xva7l-v_E5zUd27TTdJEzZGLuwNeUV2OojoMU?key=kFe-0bm0qP_I7_1RteZOAKmA)

2. Improvement needed in this example is showing more comparison to the Peer Group selected to clearly indicate where the firm is in relation to the high and low range of the peer group.


29. If Firm Approves a "Counter Proposed Rate", the system flags the rate as Approved

30. Add a notifications center with user-configurable settings. 

    1. Each user may configure for what and how (i.e., email) receive a notification for any of the following, but not limited to, examples:


1. If a new rate request is submitted by a client or firm

2. If a counter-proposed rate is submitted by a client

3. If a proposed rate is rejected by a client

4. If a client or firm sends a message (without anything rate related)

5. If client requests firm to review, negotiate and sign outside counsel guidelines


31. API to send Approved Rates by firm and timekeeperID to ELM/ebilling system. This may be configured by the client and the law firm.  

32. Confirmation loop when a law firm submits approved rates to the Client’s ebilling system, for those clients with API connection, the rate negotiation application confirms that the newly loaded rates match the newly negotiated and approved rates. 

33. Create the backend, algorithms and interface for a collaborative filtering recommendation engine for Attorneys. Using ratings provided by client users (Raters), who are typically in-house attorneys. The interface should be an optional part of onboarding of a client user with role, in-house attorney. An in-house attorney is invited to configure their ratings. Using historical billing data uploaded by the client, an in-house attorney is associated with matters. Matters are associated with law firm attorneys. Thus, during onboarding, the in-house-attorney is presented with ten attorneys they have worked with the most (based on billing data) over the past year. The in-house-attorney (called a "Rater") must rate at least five attorneys in order to configure the recommender engine. The Rater is then encouraged to rate five more to improve recommendation accuracy. Include mock data to represent in-house-attorneys and their ratings. The application will use this mock data to provide realistic testing of this capability.

34. Analytics

    1. The client makes historical billing data available, either via API or Excel upload, by named attorney and staff class.  

    2. Create a graphical representation of Rate Increase Impact, and include the ability to filter the views. Filters to include: by rate status (proposed or counter proposed, approved, all); by firm(s); by geography; by Client Department(s). Multiply the hours from the previous year by the net rate increase of the currently Proposed/approved rates. 

    3. Using hours by attorney from the previous year, calculated in total based on total hours by named attorney and associated staff class, add graph to show the impact of new proposed fees, the total approved rates, the total for rates pending (including proposed and counter proposed), and a line reflecting any defined rate rules. The default view is in total across all firms, staff classes and attorneys, but allow for drilldown using filters to view by individual firm, staff class and/or attorney.

    4. Impact analytics may be viewed as “Net” (meaning it I calculated on the difference) or “Total” (meaning the impact is the total of new proposed rates multiplied by last years hours). 

    5. Graphic and table representation of the Weighted Total Fees by user selected metric: staff class, firm, practice, peer group, geography. Whatever the user selects, the graph and table show the weighted fees (weighted fees means the rate multiplied by hours, where the hours of the subject give the corresponding fee “weight”).

    6. In addition to the standard analytics, create a “report generator” where the user may create custom reports using all available fields based on their permission. These may be graphical or table output. The user may save any report, download as PDF or Excel, or share within their organization within the application. 

35. Integrate UniCourt

    1. Create an interface for the Justice Bid application Admin to configure an API to a third party data from a service called UniCourt. The interface should allow the Justice Bid admin to map the named attorneys at each law firm Justice Bid’s database to the attorneys from UniCourt, by name and law firm. Law Firms must also have an interface to do the same mapping of their attorneys. The interface should reflect a fuzzy search to find the closest match with a degree of confidence that the Justice Bid named attorney by firm is a match to the UniCourt named attorney by firm. The user will complete the mapping by clicking to confirm. The user can select individual attorneys or multiple, and confirm in bulk. The interface must also allow the “unmapping” of a Justice Bid attorney to UniCourt attorney. 

    2. Review the API documentation for UniCourt. Before designing the backend data structure, consider the fields available from UniCourt to ensure the backend of Justice Bid is optimized to work with UniCourt's APIs. UniCourt will be used to evaluate attorney performance, thus our attorney database must align to data structures within the UniCourt API documents. 

    3. For mapped attorneys, UniCourt APIs are to be used to call recent (2yrs) the summary statistics case history of each attorney. The data structure should segment matters for the specific client viewing Justice Bid, as well as performance of the attorney overall. This should all be part of a drill down level of reporting where the client can view attorney performance at the firm level, practice area, geography, or individual attorney level. There should be a view that compares attorney performance to their bill rate. This is a metric that allows the client to compare across firms. Essentially, how active was the attorney or law firm for the cost. How effective was the attorney. 

36. Each organization, both law firms and clients, must have the ability to identify a user account with a “flag” to “Maintain Current contact Information”. These are often billing contacts and may be specific to a client by law firm. If a user is identified as such, the system will send the user an email that must be clicked to verify the user is still in their role. The system must monitor the sending email account to identify any auto-replies that say the user is no longer with the company, or the email is undeliverable. If a “Maintain Current contact information" user is deemed to no longer be current, the contact will be identified as “Find New Contact”. This will be flagged as a persistent notification for the law firm or client until the contact is replaced with a validated contact. 

37. Admin must have an interface to turn on permissions for each organization, as a client or supplier (law firm), including at what level Ai is available (i.e. Org, project, Answers, company/attorney search), and access to UniCourt data. 

38. Prepare mock dataset which will serve also as a backend database that could later be populated with real data. \[this was for my prompts to create in cursor 🙂\]

    1. Produce a realistic view for a client receiving a request, let's assume that the client has already connected their ebilling system (such as Onit, Team Connect, Legal Tracker or Bright Flag) to this Rate Negotiation application, via api, such that the historical billing information has been ingested from the client system. This data sent from the ebilling system will automatically populate the list of firms for the client. The mock attorney data should be consistent at each firm, where one attorney can work for multiple clients. To make this mock data more real, please create a mock dataset for 10 law firms, each having 6-10 staff classes, each with a 5yr history of standard and approved discounted rates, and worked hours per year ranging from 12 hours to 2000 hours. The rates and hours will be used to calculate total fees elsewhere in the application. Additionally, build a mock dataset for 10-25 named attorneys per firm, also with standard and approved rates for 5 years, and hours per year ranging from 2 hours to 750 hours. The billing history should show demonstrated rate freeze periods, of one or two years. Billing history should include a total hours billed by named attorney by month per client. 

    2. Each attorney must be associated with at least one office. Each office must have a city, state, country and geographical region. Each attorney must have a postal code. Each attorney must have at least one timekeeperID. The data structure must accommodate multiple timekeeperID’s per named attorney at each firm, which will be unique to the Attorney+firm.   

    3. For the mock dataset, add further spend history by firm indicating how many legal matters the firm worked on over the historical time period as defined by the client (default to last 12 months), the total fee value of that work based on total billed hourly work by staff class and named attorney (summarized to firm level but allow drill-down to underlying staff class and attorneys), the total value of fees that were based on Alternative Fee Arrangements.

    4. Also represent multiple geographies and currencies is the mock historical data. One named attorney may have multiple billing rates depending on the law firm's billing office. A firm may have many offices. One attorney will bill from a maximum of three offices, for example, New York, Toronto and London.

    5. Also for the mock dataset, add attorney ratings as if the data feed from the client ebillling system produces a 5 star performance rating based on reviews conducted on the attorneys by the client. 

    6. The client may also click to add a new firm, where they will be presented with a selection of firms already created in the application for other clients, and may also add a brand new firm from scratch if the client does not see their firm already available.

    7. Historical billing data will also be associated with specific legal matters. Legal matters are associated with Client Departments. This will allow the client to view proposed rates and spend by Client Department, even to the matter level. 

## 

## Planning ahead for Future Phase 

1. eBilling

   1. Brightflag is a good example of where we will go. The same data structure will need to exist to receive invoice level data from clients’ current ebilling system can be used in the future to populate with data (invoices) sent directly to this application. Our near-term objective is to have a flexible enough data structure to allow granular invoice data, including the ability to negotiate aspects of the invoice. Invoices can be sent as PDF or sent as an email. No matter the source, the invoice would be read by ai and its data stored for use. 

   2. One specific business problem to solve is during an RFP, a law firm will bid on phases to establish a fixed/capped fee by phase. Over time, new realities enter and cause a change of scope vs. the original assumptions. for example, more depositions, more expert witnesses, new evidence… Whatever the cause, the firm will submit a revised fee for a phase. Currently, there is no mechanism in any system for this to take place. This means the history is lost, there is no negotiation captured, and any benchmarking is no longer reliable and in fact may skew values.

      1. JB’s bid interface should track this

      2. if a law firm sends a message asking for a change, depending on the information contained in the message, the ai can ask follow up question and/or add contents to update the history of the matter. Even negotiate, with human-in-the-loop approval.  

   3. Easy integrations with financial/ERP systems for clients and firms

   4. Facilitate sending payments by