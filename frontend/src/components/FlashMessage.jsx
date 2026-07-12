import { useContext } from 'react';
import { FlashContext } from '../contexts/FlashProvider';


/**
 * @author ffpereira
 */
export default function FlashMessage() {
    const { flashMessage, visible, hideFlash } = useContext(FlashContext);

    const variantColors = {
        info: 'bg-blue-100 text-blue-800 border-blue-300',
        success: 'bg-green-100 text-green-800 border-green-300',
        warning: 'bg-yellow-100 text-yellow-800 border-yellow-300',
        danger: 'bg-red-100 text-red-800 border-red-300',
    };
    const colors = variantColors[flashMessage.type] || variantColors.info;

    return (
        <div className={`fixed top-4 left-1/2 -translate-x-1/2 z-50 transition-all duration-300 ease-in-out transform ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4 pointer-events-none'}`}>
            <div className={`relative px-8 py-3 border rounded-md ${colors} shadow-md`}>
                <span>{flashMessage.message}</span>
                <button onClick={hideFlash} className="absolute top-2 right-2 text-lg font-bold text-current hover:text-gray-700">&times;</button>
            </div>
        </div>
    );
}