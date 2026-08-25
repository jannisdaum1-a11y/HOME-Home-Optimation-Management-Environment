import './SidebarRight.css';

type Asset = {
    image: string;
    [key: string]: unknown;
};

const not_editable = ["image"]

type SidebarRightProps = {
    selectedAsset:Asset | null;
    setAssets: React.Dispatch<React.SetStateAction<Asset[] | []>>;
    setSelectedAsset: React.Dispatch<React.SetStateAction<Asset | null>>;
}
function SidebarRight({selectedAsset, setAssets, setSelectedAsset} : SidebarRightProps){
    const asset = selectedAsset
    
    return (
    <div className='SideBarRight'>
    {
        asset === null && <p>Wählen Sie ein beliebiges Asset aus, um verfügbare Parameter zu variieren</p>
    }
    

    {asset &&
        Object.entries(asset).map(([name, value]) => (
            <div key={name}>
                <label>{name}: </label>

                <input
                    value={String(value)}
                    disabled={not_editable.includes(name)}
                    onChange={(e) => {
                        const value = e.target.value;
                        setAssets(prev => prev.map(object =>
                            object.name === selectedAsset.name
                                ? {...object, [name]: value}
                                : object
                        ));
                        setSelectedAsset(prev => prev && prev.name === selectedAsset.name
                            ? {...prev, [name]: value}
                            : prev
                        );
                    }
                    }
                />
            </div>
        ))
    }
</div>
);
}
export default SidebarRight;