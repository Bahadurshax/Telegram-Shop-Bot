import { useEffect, useRef } from 'react'

const Modal = ({ isOpen, onClose, title, children, size = 'md' }) => {
    const modalRef = useRef()

    useEffect(() => {
        const handleEscape = (e) => {
            if (e.key === 'Escape') onClose()
        }

        if (isOpen) {
            document.addEventListener('keydown', handleEscape)
            document.body.style.overflow = 'hidden'
        }

        return () => {
            document.removeEventListener('keydown', handleEscape)
            document.body.style.overflow = 'unset'
        }
    }, [isOpen, onClose])

    if (!isOpen) return null

    const sizeClasses = {
        sm: 'max-w-md',
        md: 'max-w-lg',
        lg: 'max-w-2xl',
        xl: 'max-w-4xl',
        full: 'max-w-full mx-4'
    }

    const handleBackdropClick = (e) => {
        if (modalRef.current && !modalRef.current.contains(e.target)) {
            onClose()
        }
    }

    return (
        <div
            className="fixed inset-0 z-50 overflow-y-auto"
            aria-labelledby="modal-title"
            role="dialog"
            aria-modal="true"
        >
            <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity" aria-hidden="true" onClick={onClose}></div>

            <div className="flex min-h-full items-center justify-center p-4 sm:p-6 text-center">
                <div
                    ref={modalRef}
                    className={`
                        relative bg-white dark:bg-slate-800 rounded-2xl text-left shadow-xl transform transition-all 
                        w-full ${sizeClasses[size]} flex flex-col max-h-[90vh]
                    `}
                >
                    <div className="flex flex-col h-full overflow-hidden">
                        <div className="px-4 pt-5 pb-4 sm:p-6 sm:pb-0 flex-shrink-0">
                            {title && (
                                <div className="flex justify-between items-start mb-4">
                                    <h3 className="text-lg leading-6 font-semibold text-slate-900 dark:text-slate-100" id="modal-title">
                                        {title}
                                    </h3>
                                    <button
                                        onClick={onClose}
                                        className="bg-white dark:bg-slate-800 rounded-md text-slate-400 hover:text-slate-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                                    >
                                        <span className="sr-only">Закрыть</span>
                                        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>
                            )}
                        </div>

                        <div className="px-4 pb-4 sm:p-6 overflow-y-auto">
                            {children}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Modal
