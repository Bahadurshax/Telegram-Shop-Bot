const Loading = ({ size = 'md', className = '' }) => {
    const sizeClasses = {
        sm: 'h-8 w-8',
        md: 'h-12 w-12',
        lg: 'h-16 w-16',
        xl: 'h-32 w-32'
    }

    return (
        <div className={`flex items-center justify-center ${className}`}>
            <div className={`animate-spin rounded-full border-b-2 border-primary-600 dark:border-primary-400 ${sizeClasses[size]}`}></div>
        </div>
    )
}

export default Loading
