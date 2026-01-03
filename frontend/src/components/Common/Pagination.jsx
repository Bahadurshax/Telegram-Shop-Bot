import { PAGINATION } from '../../utils/constants'

const Pagination = ({
    currentPage,
    totalCount,
    itemsPerPage = PAGINATION.ITEMS_PER_PAGE,
    onPageChange,
    itemName = 'элементов'
}) => {
    const totalPages = Math.ceil(totalCount / itemsPerPage)

    if (totalPages <= 1) return null

    return (
        <div className="flex items-center justify-between">
            {/* Mobile pagination */}
            <div className="flex-1 flex justify-between sm:hidden">
                <button
                    onClick={() => onPageChange(Math.max(0, currentPage - 1))}
                    disabled={currentPage === 0}
                    className="relative inline-flex items-center px-4 py-2 border border-slate-300 dark:border-slate-700 text-sm font-medium rounded-lg text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    Назад
                </button>
                <button
                    onClick={() => onPageChange(Math.min(totalPages - 1, currentPage + 1))}
                    disabled={currentPage >= totalPages - 1}
                    className="ml-3 relative inline-flex items-center px-4 py-2 border border-slate-300 dark:border-slate-700 text-sm font-medium rounded-lg text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    Вперед
                </button>
            </div>

            {/* Desktop pagination */}
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                    <p className="text-sm text-slate-700 dark:text-slate-400">
                        Показано <span className="font-semibold text-slate-900 dark:text-slate-100">{currentPage * itemsPerPage + 1}</span> до{' '}
                        <span className="font-semibold text-slate-900 dark:text-slate-100">
                            {Math.min((currentPage + 1) * itemsPerPage, totalCount)}
                        </span>{' '}
                        из <span className="font-semibold text-slate-900 dark:text-slate-100">{totalCount}</span> {itemName}
                    </p>
                </div>
                <div>
                    <nav className="relative z-0 inline-flex rounded-lg shadow-sm -space-x-px" aria-label="Pagination">
                        <button
                            onClick={() => onPageChange(Math.max(0, currentPage - 1))}
                            disabled={currentPage === 0}
                            className="relative inline-flex items-center px-2 py-2 rounded-l-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm font-medium text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            <span className="sr-only">Предыдущая</span>
                            <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                        </button>
                        {Array.from({ length: Math.min(PAGINATION.MAX_PAGE_BUTTONS, totalPages) }, (_, i) => {
                            // Logic to show pages around current page could be more complex, 
                            // keeping simple logic from before but modernized styling
                            const pageNum = currentPage < 3 ? i : currentPage - 2 + i
                            if (pageNum >= totalPages) return null

                            const isActive = pageNum === currentPage
                            return (
                                <button
                                    key={pageNum}
                                    onClick={() => onPageChange(pageNum)}
                                    className={`
                                        relative inline-flex items-center px-4 py-2 border text-sm font-medium transition-colors
                                        ${isActive
                                            ? 'z-10 bg-primary-50 dark:bg-primary-900/20 border-primary-500 text-primary-600 dark:text-primary-400'
                                            : 'bg-white dark:bg-slate-800 border-slate-300 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700'
                                        }
                                    `}
                                >
                                    {pageNum + 1}
                                </button>
                            )
                        })}
                        <button
                            onClick={() => onPageChange(Math.min(totalPages - 1, currentPage + 1))}
                            disabled={currentPage >= totalPages - 1}
                            className="relative inline-flex items-center px-2 py-2 rounded-r-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm font-medium text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            <span className="sr-only">Следующая</span>
                            <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                            </svg>
                        </button>
                    </nav>
                </div>
            </div>
        </div>
    )
}

export default Pagination
