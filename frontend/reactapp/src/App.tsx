import { useState } from 'react'
import './App.css'

import SidebarLeft from './SidebarLeft'
import SidebarRight from './SidebarRight'
import DragAndDrop from './DragAndDrop'

type Asset = {
    image: string;
    [key: string]: unknown;
};

function App() {
    const [objects, setObjects] = useState<Asset[]>([]);
    const [selectedObject, setSelectedObject] = useState<Asset|null>(null)
    
    return (
        <div className="MainContent">
        <aside>
            <SidebarLeft></SidebarLeft>
        </aside>
        
        <div className='Workspace'>
            <DragAndDrop 
            objects={objects}
            setObjects={setObjects}
            setSelectedObject={setSelectedObject}
            ></DragAndDrop>
        </div>

        <aside>
            <SidebarRight selectedAsset={selectedObject} setSelectedAsset={setSelectedObject} setAssets={setObjects}></SidebarRight>
        </aside>
        </div>  
    )
}

export default App
