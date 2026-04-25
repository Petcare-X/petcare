type EmptyStateProps = {
    title: string;
    description: string;
    actionText?: string;
    onAction?: () => void;
};

export function EmptyState({
    title,
    description,
    actionText,
    onAction,
}: EmptyStateProps) {
    return (
        <div className="empty-state">
            <div className="empty-state-icon">+</div>
            <h3 className="empty-state-title">{title}</h3>
            <p className="empty-state-description">{description}</p>
            {actionText && onAction ? (
                <button className="empty-state-action" type="button" onClick={onAction}>
                    {actionText}
                </button>
            ) : null}
        </div>
    );
}
