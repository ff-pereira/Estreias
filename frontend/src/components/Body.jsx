import FlashMessage from './FlashMessage';

/**
 * @author ffpereira
 */
export default  function Body({ children }) {
    return (
        <div className="mx-2 px-2">
            <div className="flex w-full justify-center">
                <div className="md:mx-2 md:px-2 flex-1">
                    <FlashMessage />
                    {children}
                </div>
            </div>
        </div>
    );
}