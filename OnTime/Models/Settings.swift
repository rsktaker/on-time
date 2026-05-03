import Foundation

struct OnTimeConfig: Codable, Equatable {
    var bufferMinutes: Int
    var excludedCalendarTitles: [String]
    var skipAllDayEvents: Bool

    static let `default` = OnTimeConfig(
        bufferMinutes: AppConstants.defaultBufferMinutes,
        excludedCalendarTitles: [],
        skipAllDayEvents: true
    )
}
